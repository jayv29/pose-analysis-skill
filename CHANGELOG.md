# Changelog

## Unreleased

### Added

- GitHub-ready repository presentation with bilingual README upgrades, source-backed knowledge-base highlights, demo reports, GitHub Pages showcase, issue templates, license, contribution guide, security/privacy notes, and social preview assets.

## [3.0.0] - 2026-05-25

### Changed

- Migrated the project from an OpenClaw-style skill to a Codex skill.
- Replaced direct model-provider calls with Codex current-session analysis.
- Defaulted the iPhone workflow to iCloud Drive `PoseAnalysis/Inbox` and `PoseAnalysis/Report`.
- Added deterministic report skeleton generation, quality-gate metadata, and same-template history indexing.

### Added

- Coach-grade Chinese report workflow for foil fencing, top-rope/lead climbing, and youth fitness.
- Video quality gate with `可评分`, `部分可评分`, and `不可评分` outcomes.
- Advanced sport knowledge base:
  - foil fencing rubric and phase diagnosis
  - climbing rubric for top-rope, lead, crux, footwork, and center-of-mass control
  - youth fitness rubric for squat, split squat/lunge, push-up, plank/hollow, jump landing, and single-leg control
- Professional analysis standards, final-report quality rules, phase recognition, privacy rules, and history-comparison rules.
- Unit tests for output paths, context parsing, quality gates, unscorable reports, history indexing, and symlink-safe filenames.

### Fixed

- Prevented same-day report and JSON outputs from overwriting existing files.
- Rendered missing metrics as `N/A` instead of fake zero-degree evidence.
- Cleaned temporary JSON handling in the shell runner.
- Hardened model download behavior with fail-fast curl, temporary files, non-empty checks, and atomic moves.

## [2.0.0] - 2026-02-18

### Added

- Geometric analysis core for biomechanical metrics such as knee angles and hip height.
- Multi-sport support for fencing, fitness, climbing, running, and skiing.
- Structured coach-style reports with scoring tables and prioritized advice.

### Improved

- Keyframe detection for the lowest center of gravity.
- Token-optimized JSON summaries for AI analysis.
