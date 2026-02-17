# Changelog

## [2.0.0] - 2026-02-18

### 🚀 New Features

- **Geometric Analysis Core**: Added `GeometryUtils` in Python to calculate biomechanical metrics locally (e.g., knee angles, hip height). No longer relies on raw coordinates.
- **Multi-Sport Support**: Added expert role switching for 5 sports:
    - 🤺 **Fencing**: Focus on Lunge Depth (En Garde).
    - 🏋️ **Fitness**: Focus on Squat/Lunge mechanics.
    - 🧗 **Climbing**: Focus on Hip-to-Wall distance.
    - 🏃 **Running**: Focus on Cadence and Oscillation.
    - ⛷️ **Skiing**: Focus on Parallel Legs and Angulation.
- **Professional Report Format**: Updated LLM system prompts to generate structured, coach-style reports with scoring tables and prioritized advice.

### 🛠 Improvements

- **Keyframe Detection**: Automatically identifies the "Moment of Truth" (e.g., lowest center of gravity) for analysis.
- **Token Optimization**: Reduced JSON output size by 70% by summarizing frames before sending to LLM.
