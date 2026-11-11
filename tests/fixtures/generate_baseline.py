"""Freeze synthetic expectations from the PR base, never from the changed code."""
import ast
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
BASE = 'bb6f0b5f7955c09b36db66202e77d29ed3c7d9ad'
def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=root).decode('utf-8')
quality = types.ModuleType('baseline_quality')
exec(compile(original('src/data_quality.py'), 'baseline_quality', 'exec'), quality.__dict__)
risk = types.ModuleType('baseline_risk')
risk_text = original('src/risk_scoring.py')
exec(compile(risk_text, 'baseline_risk', 'exec'), risk.__dict__)
risk.add_data_quality_flags = quality.add_data_quality_flags
risk.save_data_quality_outputs = quality.save_data_quality_outputs
sensitivity = types.ModuleType('baseline_sensitivity')
exec(compile(original('src/sensitivity_analysis.py'), 'baseline_sensitivity', 'exec'), sensitivity.__dict__)

# Extract only the base revision's input schema, not its scoring expressions.
function = next(n for n in ast.parse(risk_text).body if isinstance(n, ast.FunctionDef) and n.name == 'build_scores')
columns = []
for node in function.body:
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id.endswith('_cols'):
            if node.lineno < 279:
                columns.extend(ast.literal_eval(node.value))
columns = list(dict.fromkeys(columns))
n = 5
rng = np.random.default_rng(4271)
complete = pd.DataFrame({col: rng.integers(0, 30, n).astype(float) for col in columns})
complete['county'] = [f'Synthetic {x}' for x in 'ABCDE']
complete['population'] = [10000, 20000, 35000, 50000, 75000]
complete['median_household_income'] = [45000, 65000, 51000, 84000, 72000]
complete['poverty_rate'] = [.2, .11, .15, .07, .09]
complete['unemployment_rate'] = [.05, .03, .04, .02, .025]
complete['rent_burden_rate'] = [.45, .3, .4, .25, .35]
complete['crime_population_2024'] = complete['population']
soc = complete[['county','population','median_household_income','poverty_rate','unemployment_rate','rent_burden_rate']].copy()
mixed = complete.copy()
mixed.loc[0, 'bank_branch_count'] = np.nan
mixed.loc[1, 'homicide_count'] = np.nan
mixed.loc[2, 'population'] = 0
mixed.loc[3, 'median_household_income'] = np.nan
mixed = mixed.drop(columns=['gang_explosive_total_offense_count', 'power_outage_event_count'])

fixture = {'base_commit': BASE, 'seed': 4271, 'cases': []}
with tempfile.TemporaryDirectory() as directory:
    risk.TABLES_DIR = quality.TABLES_DIR = sensitivity.TABLES_DIR = Path(directory)
    for name, frame in [('socioeconomic_only', soc), ('complete', complete), ('mixed_missing', mixed)]:
        with contextlib.redirect_stdout(io.StringIO()):
            scores = risk.build_scores(frame)
            quality_columns = set(quality.save_data_quality_outputs(scores)) - {'county', 'population'}
            results = sensitivity.build_sensitivity_results(scores)
            ranks = sensitivity.build_rank_stability_table(results)
        core = scores.drop(columns=list(quality_columns), errors='ignore')
        scenario_core = results.drop(columns=['model_confidence'])
        case = {'name': name, 'input': json.loads(frame.to_json(orient='split', double_precision=15)),
                'scores': json.loads(core.to_json(orient='split', double_precision=15)),
                'scenarios': json.loads(scenario_core.to_json(orient='split', double_precision=15)),
                'ranks': json.loads(ranks.to_json(orient='split', double_precision=15))}
        fixture['cases'].append(case)
target = root / 'tests/fixtures/scoring_base.json'
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(fixture, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps({'bytes': target.stat().st_size, 'cases': len(fixture['cases']), 'score_fields': len(fixture['cases'][0]['scores']['columns']), 'scenarios_per_case': 10}))
