"""Read-only formula audit of the pinned release; never invokes the pipeline."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).with_name("config.json")


@dataclass(frozen=True)
class Leaf:
    name: str
    expression: str
    line: int
    stored_column: str | None
    input_column: str | None = None


@dataclass
class Graph:
    edges: dict[str, dict[str, Fraction]]
    leaves: dict[str, Leaf]
    lines: dict[str, int]

    def paths(self, root: str, coefficient: Fraction = Fraction(1),
              trail: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Fraction]]:
        if root in trail:
            raise ValueError(f"Cycle at {root}")
        trail = (*trail, root)
        if root in self.leaves:
            return [(trail, coefficient)]
        if root not in self.edges:
            raise ValueError(f"Unresolved score {root}")
        return [path for child, weight in self.edges[root].items()
                for path in self.paths(child, coefficient * weight, trail)]


def add(left: dict[str, Fraction], right: dict[str, Fraction]) -> dict[str, Fraction]:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
    return result


def field(node: ast.AST) -> str | None:
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value if isinstance(node.slice.value, str) else None
    return None


def verify_sources(root: Path, config: dict) -> None:
    for name, expected in config["source_sha256_lf"].items():
        actual = hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
        if actual != expected:
            raise ValueError(f"Pinned source changed: {name}; review before extending audit")


def build_graph(root: Path, config: dict, regime: str) -> tuple[Graph, dict]:
    """Extract convex sums; stop at normalization, not at raw observed counts.

    Source hashes bind the explicitly handled cash mean and conditional override.
    No arbitrary source code is executed, and unsupported reachable syntax fails.
    """
    verify_sources(root, config)
    if regime not in {"phase6_active", "fema_fallback"}:
        raise ValueError(regime)
    tree = ast.parse((root / "src/risk_scoring.py").read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build_scores")
    definitions: dict[str, ast.AST] = {}
    lines: dict[str, int] = {}
    cash_columns: list[str] = []
    for stmt in function.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if isinstance(target, ast.Name) and target.id == "cash_cols":
            cash_columns = ast.literal_eval(stmt.value)
        name = field(target)
        if name:
            if name in definitions:
                raise ValueError(f"Repeated direct definition: {name}")
            definitions[name] = stmt.value
            lines[name] = stmt.lineno
    graph = Graph({}, {}, lines)
    cash_loop_line = next(n.lineno for n in ast.walk(function)
                          if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                          and n.func.id == "minmax_score" and ast.unparse(n) == "minmax_score(df[col])")
    for column in cash_columns:
        name = f"{column}_score"
        graph.leaves[name] = Leaf(name, f"minmax_score(df[{column!r}])",
                                  cash_loop_line, name)
    graph.edges["cash_intensive_retail_score"] = {
        f"{col}_score": Fraction(1, len(cash_columns)) for col in cash_columns
    }

    def parse(node: ast.AST) -> dict[str, Fraction]:
        name = field(node)
        if name:
            return {name: Fraction(1)}
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return add(parse(node.left), parse(node.right))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            if not isinstance(node.left, ast.Constant):
                raise ValueError("Expected literal left coefficient")
            weight = Fraction(str(node.left.value))
            return {name: weight * value for name, value in parse(node.right).items()}
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "minmax_score":
            source = field(node.args[0])
            if source is None or node.keywords:
                raise ValueError("Unsupported inline normalization")
            name = f"normalized::{source}"
            graph.leaves[name] = Leaf(name, ast.unparse(node), node.lineno, None, source)
            return {name: Fraction(1)}
        raise ValueError(f"Unsupported reachable formula at line {node.lineno}: {ast.unparse(node)}")

    def resolve(name: str, active: tuple[str, ...] = ()) -> None:
        if name in active:
            raise ValueError(f"Cycle at {name}")
        if name in graph.leaves:
            return
        if name not in graph.edges:
            node = definitions[name]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "minmax_score":
                graph.leaves[name] = Leaf(name, ast.unparse(node), lines[name], name)
                return
            graph.edges[name] = parse(node)
        for child in graph.edges[name]:
            resolve(child, (*active, name))

    if regime == "fema_fallback":
        graph.edges[config["disruption_score"]] = {config["fallback_score"]: Fraction(1)}
    scenario_tree = ast.parse((root / "src/sensitivity_analysis.py").read_text(encoding="utf-8"))
    scenarios = next(ast.literal_eval(n.value) for n in scenario_tree.body
                     if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCENARIOS" for t in n.targets))
    resolve(config["final_score"])
    for scenario, weights in scenarios.items():
        scenario_root = f"scenario::{scenario}"
        graph.edges[scenario_root] = {name: Fraction(str(weight)) for name, weight in weights.items()}
        resolve(scenario_root)
    for name, weights in graph.edges.items():
        if sum(weights.values()) != 1 or any(w < 0 for w in weights.values()):
            raise ValueError(f"Non-convex equation: {name}")
    return graph, scenarios


def weights(graph: Graph, root: str) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for trail, value in graph.paths(root):
        result = add(result, {trail[-1]: value})
    if sum(result.values()) != 1:
        raise ValueError("Terminal weights do not sum to one")
    return result


def node_weights(graph: Graph, root: str) -> dict[str, Fraction]:
    """All incoming paths to each internal node; levels must not be added."""
    result: dict[str, Fraction] = {}

    def visit(name: str, coefficient: Fraction) -> None:
        result[name] = result.get(name, Fraction(0)) + coefficient
        for child, weight in graph.edges.get(name, {}).items():
            visit(child, coefficient * weight)

    visit(root, Fraction(1))
    return result


def leaf_values(graph: Graph, frame: pd.DataFrame) -> dict[str, pd.Series]:
    result = {}
    for name, leaf in graph.leaves.items():
        if leaf.stored_column:
            result[name] = pd.to_numeric(frame[leaf.stored_column], errors="raise")
        else:
            values = pd.to_numeric(frame[leaf.input_column], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)
            lo, hi = values.min(), values.max()
            result[name] = pd.Series(50.0, index=frame.index) if lo == hi else 100 * (values - lo) / (hi - lo)
    return result


def active_mask(frame: pd.DataFrame, root: Path, config: dict) -> pd.Series:
    """Read the pinned positive-signal groups, retaining group-sum semantics."""
    verify_sources(root, config)
    tree = ast.parse((root / "src/risk_scoring.py").read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build_scores")
    named_lists = {}
    signal = None
    for stmt in function.body:
        if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
            if isinstance(stmt.value, ast.List):
                try:
                    named_lists[stmt.targets[0].id] = ast.literal_eval(stmt.value)
                except ValueError:
                    pass
            if stmt.targets[0].id == "phase6_positive_signal":
                signal = stmt.value
    if signal is None:
        raise ValueError("Missing conditional signal")

    def evaluate(node: ast.AST) -> pd.Series:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return evaluate(node.left) | evaluate(node.right)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_has_positive_signal":
            argument = node.args[1]
            columns = named_lists[argument.id] if isinstance(argument, ast.Name) else ast.literal_eval(argument)
            # Saved scored frames contain all these fields; omission is an error.
            return frame[columns].apply(pd.to_numeric, errors="raise").sum(axis=1) > 0
        raise ValueError("Unsupported conditional expression")

    return evaluate(signal)


def validate_saved(frame: pd.DataFrame, scenario_frame: pd.DataFrame,
                   root: Path, config: dict) -> dict:
    """Reconstruct from saved normalized leaves, without rewriting any scores."""
    if frame["county"].duplicated().any():
        raise ValueError("Duplicate counties")
    active = active_mask(frame, root, config)
    errors = []
    counts = {}
    for regime, mask in [("phase6_active", active), ("fema_fallback", ~active)]:
        graph, scenarios = build_graph(root, config, regime)
        values = leaf_values(graph, frame)  # Normalize over the full frame before selecting rows.
        counts[regime] = int(mask.sum())
        for label in ["final", *scenarios]:
            score_root = config["final_score"] if label == "final" else f"scenario::{label}"
            prediction = sum(float(w) * values[name] for name, w in weights(graph, score_root).items())
            if label == "final":
                expected = frame[config["final_score"]]
            else:
                subset = scenario_frame[scenario_frame["scenario"] == label]
                if subset["county"].duplicated().any() or set(subset["county"]) != set(frame["county"]):
                    raise ValueError("Scenario county mismatch")
                expected = frame["county"].map(subset.set_index("county")["scenario_score"])
            np.testing.assert_allclose(prediction[mask], expected[mask], rtol=config["rtol"], atol=config["atol"])
            if mask.any():
                errors.append(float((prediction[mask] - expected[mask]).abs().max()))
    return {"rows": len(frame), "regimes": counts, "baseline_and_scenarios": 11,
            "max_absolute_error": max(errors, default=0.0), "passed": True}


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-scores", type=Path)
    parser.add_argument("--saved-scenarios", type=Path)
    args = parser.parse_args()
    if bool(args.saved_scores) != bool(args.saved_scenarios):
        parser.error("Supply both saved tables or neither")
    config = json.loads(CONFIG_PATH.read_text())
    target = ROOT / config["output_dir"]
    target.mkdir(parents=True, exist_ok=True)
    terminal_rows, path_rows, node_rows, equation_rows = [], [], [], []
    for regime in ("phase6_active", "fema_fallback"):
        graph, scenarios = build_graph(ROOT, config, regime)
        for label in ["final", *scenarios]:
            score_root = config["final_score"] if label == "final" else f"scenario::{label}"
            trails = graph.paths(score_root)
            for name, value in sorted(weights(graph, score_root).items()):
                leaf = graph.leaves[name]
                terminal_rows.append(dict(regime=regime, score=label, indicator=name,
                                          coefficient_exact=str(value), percent=float(value * 100),
                                          path_count=sum(t[-1] == name for t, _ in trails),
                                          normalization=leaf.expression, source_line=leaf.line))
            for trail, value in trails:
                path_rows.append(dict(regime=regime, score=label, path=" -> ".join(trail),
                                      coefficient_exact=str(value), percent=float(value * 100)))
            for name, value in sorted(node_weights(graph, score_root).items()):
                node_rows.append(dict(regime=regime, score=label, node=name,
                                      kind="terminal" if name in graph.leaves else "composite",
                                      coefficient_exact=str(value), percent=float(value * 100)))
        for name, children in sorted(graph.edges.items()):
            for child, value in children.items():
                equation_rows.append(dict(regime=regime, parent=name, child=child,
                                          coefficient_exact=str(value), source_line=graph.lines.get(name, "scenario dictionary")))
    for filename, rows in [("terminal_weights.csv", terminal_rows), ("paths.csv", path_rows),
                           ("node_weights.csv", node_rows), ("equations.csv", equation_rows)]:
        write_csv(target / filename, rows)
    fixture_path = ROOT / "tests/fixtures/scoring_base.json"
    fixture = json.loads(fixture_path.read_text())
    def frame(snapshot: dict) -> pd.DataFrame:
        return pd.DataFrame(snapshot["data"], columns=snapshot["columns"])
    validation = {case["name"]: validate_saved(frame(case["scores"]), frame(case["scenarios"]), ROOT, config)
                  for case in fixture["cases"]}
    record = {"baseline_commit": config["baseline_commit"], "source_sha256_lf": config["source_sha256_lf"],
              "synthetic_fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
              "rtol": config["rtol"], "atol": config["atol"], "synthetic_reconciliation": validation,
              "scope": "Normalized-score coefficient audit; no pipeline, source fetch, ranking change or raw-count marginal effects."}
    if args.saved_scores:
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.saved_scores, args.saved_scenarios]}
        record["published_reconciliation"] = validate_saved(pd.read_csv(args.saved_scores), pd.read_csv(args.saved_scenarios), ROOT, config)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.saved_scores, args.saved_scenarios]}
        assert before == after
        record["saved_inputs_sha256"] = before
    (target / "verification.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
