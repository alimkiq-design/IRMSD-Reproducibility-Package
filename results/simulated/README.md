# Simulated sprint-pilot output

The input file contains 72 **synthetic** sprint records from 12 simulated teams (six teams in each condition, six sprints per team). The analysis output is generated from that synthetic input using the script in `sprint_pilot/scripts/analyze_sprint_pilot.py`.

## Diagnostics

Five of six mixed-effects model fits failed with singular-matrix errors. The schedule-variance model returned a numerical fit but reported a singular random-effects covariance, a boundary estimate, and a non-positive-definite Hessian. Its inferential output is therefore not treated as reliable confirmatory evidence. Mann–Whitney U and Cohen's d use team-level means (n=6 per group) rather than treating repeated sprint rows as independent.

These results demonstrate code-path execution only. They are not observations from real software teams, do not establish causal effects, and must not be presented in the manuscript as empirical validation.
