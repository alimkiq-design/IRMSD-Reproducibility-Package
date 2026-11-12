# Methodology summary

This document records definitions stated in the accompanying manuscript. It is not a substitute for the full protocol or source-code implementation.

## Architecture
1. Artifact ingestion and linking.
2. NLP candidate risk extraction.
3. Human validation and quantitative screening.
4. Deterministic workflow gating and monitoring.

## Candidate risk extraction
The manuscript specifies multi-label BERT-base-uncased candidate classification over twelve risk categories. Model confidence scores are candidate scores and must not be interpreted as risk severity or event probability.

## Human screening
A human reviewer assesses probability `P` and impact `I` on five-point scales. The ordinal screening index is `R = P × I`, from 1 to 25.

## Effort adjustment
`E_adj = E_init × (1 + alpha_cal × (R_max / 25))`, where `0 < alpha_cal <= 0.50`.

## Workflow gates
- Low (1–6): Ready_for_Sprint.
- Medium (7–14): In_Progress (Review Gate).
- High (15–25): Blocked_Spike.

## Evidence boundaries
The manuscript reports prototype regression checks, an illustrative task walkthrough, and a synthetic sprint-data pipeline check. These are different evidence types and must remain separately labelled. The synthetic sprint analysis is not a live-team trial. The manuscript presents expert dataset labelling, model benchmarking, and live team trials as a future validation roadmap.
