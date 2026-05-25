#!/bin/bash
set -euo pipefail

ICLOUD_ROOT="$HOME/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis"
INBOX_DIR="${POSE_ANALYSIS_INBOX_DIR:-$ICLOUD_ROOT/Inbox}"
REPORT_DIR="${POSE_ANALYSIS_OUTPUT_DIR:-$ICLOUD_ROOT/Report}"
export POSE_ANALYSIS_OUTPUT_DIR="$REPORT_DIR"

usage() {
  echo "用法: ./run_skill.sh <视频路径>" >&2
  echo "   或: ./run_skill.sh --latest" >&2
  echo "默认 Inbox: $INBOX_DIR" >&2
  echo "默认 Report: $POSE_ANALYSIS_OUTPUT_DIR" >&2
}

find_latest_video() {
  if [ ! -d "$INBOX_DIR" ]; then
    echo "错误: Inbox 目录不存在: $INBOX_DIR" >&2
    return 1
  fi
  find "$INBOX_DIR" -maxdepth 1 -type f \( \
    -iname "*.mov" -o -iname "*.mp4" -o -iname "*.m4v" -o -iname "*.avi" \
  \) -print0 | while IFS= read -r -d '' file; do
    printf "%s\t%s\n" "$(stat -f "%m" "$file")" "$file"
  done | sort -nr | head -n 1 | cut -f 2-
}

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

if [ "$1" = "--latest" ] || [ "$1" = "latest" ]; then
  VIDEO_PATH="$(find_latest_video)"
  if [ -z "$VIDEO_PATH" ]; then
    echo "错误: Inbox 中没有找到支持的视频文件。" >&2
    exit 1
  fi
else
  VIDEO_PATH="$1"
fi

if [ ! -f "$VIDEO_PATH" ]; then
  echo "错误: 视频文件不存在: $VIDEO_PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POSE_JSON_TMP="$(mktemp /tmp/pose-analysis.XXXXXX)"
POSE_JSON_TMP_JSON="${POSE_JSON_TMP}.json"
mv "$POSE_JSON_TMP" "$POSE_JSON_TMP_JSON"
POSE_JSON_TMP="$POSE_JSON_TMP_JSON"
cleanup() {
  rm -f "$POSE_JSON_TMP"
}
trap cleanup EXIT

PYTHON_BIN="${POSE_ANALYSIS_PYTHON:-$HOME/.venv-pose/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3)"
fi

export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/pose-analysis-mpl-cache}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/pose-analysis-cache}"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME" "$POSE_ANALYSIS_OUTPUT_DIR"

"$PYTHON_BIN" "$SCRIPT_DIR/pose_analyzer.py" "$VIDEO_PATH" > "$POSE_JSON_TMP"
"$PYTHON_BIN" "$SCRIPT_DIR/report_formatter.py" "$VIDEO_PATH" "$POSE_JSON_TMP"
