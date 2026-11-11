# Census clarification on unpublished 2023 CBP cells

Recorded October 28, 2026; updated October 29, 2026. Documentation only; no code, input values,
availability flags, confidence labels, scores, rankings, or generated outputs
are changed by this note.

## Source and scope

The Census County Business Patterns team replied on October 28, 2026 at
21:05:11 UTC (4:05:11 p.m. America/Chicago), signed John, to the inquiry
“2023 CBP: interpreting unpublished Tennessee county-industry cells.”
The reply was checked against the user-provided two-page email PDF and the
received Gmail message. Correspondence is retained locally, not committed here.
The PDF SHA-256 is
`69346eb466dca1e34494f43d65d61e1eb53d9a269d71d599478e5b83c4d5c0cf`.

The inquiry concerned 2023 ESTAB for Tennessee, county `*`, LFO=001,
EMPSZES=001, and NAICS2017 453991, 451110, 453310, 447110, 445120,
522291, 812310, and 441120. The preceding audit retrieved 368 of 760
county-industry pairs; 392 had no returned row.

## Source-owner clarification

- John states that each of those 392 omitted pairs represents 0, 1, or 2
  establishments and that no other condition causes omission under the stated
  2023 query conditions.
- There is no published indicator distinguishing zero from one or two
  establishments for these omitted cells.
- He identifies the [CBP methodology page](https://www.census.gov/programs-surveys/cbp/technical-documentation/methodology.html)
  as the applicable documentation for 2023. He explains that its revision
  disclaimer concerns the changed disclosure-avoidance methodology for 2024
  and subsequent releases, rather than invalidating the 2023 guidance.

These are attributed findings from dated correspondence. Do not extend the
omission rule to other releases, measures, filters, or datasets without evidence.

## Threshold question closed — October 29, 2026

Answer 1 says “fewer than three establishments” and explicitly lists 0, 1, 2.
Answer 2 says “greater than 3 establishments” when describing published cells.
John explicitly corrected the second answer in his October 29 reply: cells with
**three or more establishments, including exactly three, are published** in the
2018–2023 timeframe. Only cells with zero, one, or two establishments are omitted
in 2023. The publication-threshold question is closed by source-owner confirmation.

The updated four-page correspondence PDF includes this reply on page 4 and has
SHA-256 `fdf4e1ff9285f0efa206f9d50402de77b94d36103a71b831f5172cacfb50b5b9`.
This is a new export of the expanded thread, distinct from the October 28 PDF
identified above. The October 29 reply was also checked in Gmail.

Census clarified its data methodology; this is not a review, validation, or
endorsement of the model. John expressed interest and an intention to forward
the repository to colleagues; completed forwarding or review is not established.

## Analytical disposition

For documentation, classify the absent 2023 pairs as **unpublished; 0–2
establishments according to Census correspondence; exact count unavailable**,
with the publication threshold now confirmed. This supersedes generic uncertainty
about why these specific rows are absent, not uncertainty about their exact counts.
Do not assign an observed zero, a midpoint, or a reconstructed value. Exact-count
coverage remains incomplete; the existing availability flags and confidence
labels are unchanged. Existing numeric zero fallbacks remain computational
defaults, not observed establishment counts.

The reply does not authenticate the original cache's retrieval year or vintage.
It does not resolve TBI, ACLED, or disruption-layer gaps. Any use of these bounds
to change scores or run sensitivity scenarios requires separate review.
The earlier numerical-parity results remain historical verification results;
no model rerun is required for this documentation-only addition.
