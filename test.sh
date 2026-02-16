#!/bin/bash
# 快速测试姿态分析脚本

source ~/.venv-pose/bin/activate

VIDEO_DIR=~/Videos

echo "=== 姿态分析 Skill ==="
echo ""
echo "视频存放目录: $VIDEO_DIR"
echo ""
echo "用法:"
echo "  告诉贾维斯: '用姿态分析 skill 分析 ~/Videos/你的训练视频.mp4'"
echo ""
echo "手动运行:"
echo "  python3 ~/.openclaw/workspace/skills/pose-analysis/pose_analyzer.py <视频路径>"
echo ""
echo "示例:"
echo "  python3 ~/.openclaw/workspace/skills/pose-analysis/pose_analyzer.py ~/Videos/击剑训练.mp4"
