#!/bin/bash
set -euo pipefail

MODEL_URL="https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task"
MODEL_PATH="${POSE_LANDMARKER_MODEL:-/tmp/pose_landmarker.task}"
MODEL_DIR="$(dirname "$MODEL_PATH")"

mkdir -p "$MODEL_DIR"
TMP_MODEL="$(mktemp "$MODEL_DIR/.pose_landmarker.XXXXXX")"
cleanup() {
  rm -f "$TMP_MODEL"
}
trap cleanup EXIT

curl -fL --retry 3 -o "$TMP_MODEL" "$MODEL_URL"
if [ ! -s "$TMP_MODEL" ]; then
  echo "下载失败：模型文件为空" >&2
  exit 1
fi
mv "$TMP_MODEL" "$MODEL_PATH"
trap - EXIT
echo "$MODEL_PATH"
