> Architecture Frozen — Deterministic Reasoning Baseline
>
> This version represents a stable, reproducible reasoning system.
> Core behavior, execution order, and reasoning semantics are frozen.
> Future changes must be versioned and justified.

## Versioned Extensions

### v1.1.0 — Cross-Run Reasoning Consistency & Contradiction Detection

Extends the frozen v1.0 baseline with historical reasoning comparison:
- Computes deterministic "reasoning signatures" from dataset hash and hypothesis outcomes
- Compares current run against prior runs to detect exact matches, partial reinforcement, and contradictions
- Appends "Historical Consistency Check" narrative explaining reasoning alignment
- No changes to core detection, hypothesis generation, or scoring logic
- All comparisons remain deterministic and reproducible
