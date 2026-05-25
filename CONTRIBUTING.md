# Contributing

PoseAnalysis is a Codex skill for local-first sports technique analysis. Contributions are welcome when they improve evidence quality, reporting clarity, privacy, or sport-specific rubrics.

## Good Contributions

- Better video-quality gate rules for single-camera youth training videos.
- Better phase detection logic for foil fencing, lead/top-rope climbing, or youth fitness templates.
- Higher-quality report templates with clear evidence labels.
- Anonymous demo reports, capture-angle guides, or validation notes.
- Tests for report formatting, history comparison, parsing, and quality gating.

## Contribution Rules

- Do not include identifiable child videos, faces, names, club names, school names, or exact home/training locations.
- Do not claim medical diagnosis, injury diagnosis, or official federation certification.
- Cite sources when adding sport-science, biomechanics, coaching, or competition-rule knowledge.
- Keep Codex as the reasoning layer. This repository should remain a skill, not a standalone SaaS product.
- Prefer deterministic scripts for extraction and structured references for expert judgment.

## Local Checks

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

PYTHONPYCACHEPREFIX=/tmp/pose-analysis-pycache python3 -m py_compile \
  pose-analysis/scripts/pose_analyzer.py \
  pose-analysis/scripts/report_formatter.py \
  pose-analysis/scripts/analyze_pose.py

bash -n pose-analysis/scripts/run_skill.sh
bash -n pose-analysis/scripts/download_pose_model.sh

python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py pose-analysis
```

## Source Standard

When adding professional knowledge, include:

- source name and URL or DOI
- sport or template
- observable video evidence
- confidence limits
- whether it is appropriate for a 10-year-old athlete

See [`docs/references/professional-sources.md`](docs/references/professional-sources.md).
