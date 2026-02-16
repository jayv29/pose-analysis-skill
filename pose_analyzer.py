#!/usr/bin/env python3
"""
Pose Analysis Script - 简化版
用 MediaPipe 分析训练视频姿态，输出关键点数据
"""

import sys
import json
import os
from pathlib import Path

# 虚拟环境路径
VENV_PATH = Path.home() / ".venv-pose"


def extract_pose(video_path: str) -> dict:
    """用 MediaPipe 提取姿态关键点"""
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    import mediapipe as mp
    import cv2
    
    print(f"正在处理视频: {video_path}", file=sys.stderr)
    
    # 配置 PoseLandmarker
    base_options = python.BaseOptions(model_asset_path='/tmp/pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1
    )
    
    detector = vision.PoseLandmarker.create_from_options(options)
    
    # 读取视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频 {video_path}", file=sys.stderr)
        return {}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    landmarks_data = []
    
    print(f"视频 FPS: {fps}", file=sys.stderr)
    
    while cap.isOpened() and frame_count < 300:  # 最多分析前300帧（约10秒）
        success, image = cap.read()
        if not success:
            break
        
        # 每秒采样一帧
        if frame_count % int(fps) == 0:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # 检测姿态
            result = detector.detect_for_video(mp_image, int(frame_count * 1000 / fps))
            
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = []
                for lm in result.pose_landmarks[0]:
                    landmarks.append({
                        "x": round(lm.x, 4),
                        "y": round(lm.y, 4),
                        "z": round(lm.z, 4) if hasattr(lm, 'z') and lm.z else 0
                    })
                
                landmarks_data.append({
                    "frame": frame_count,
                    "landmarks": landmarks
                })
                print(f"第 {frame_count} 帧: 检测到人体姿态", file=sys.stderr)
            else:
                print(f"第 {frame_count} 帧: 未检测到人体", file=sys.stderr)
        
        frame_count += 1
        
        if frame_count % 60 == 0:
            print(f"已处理 {frame_count} 帧...", file=sys.stderr)
    
    cap.release()
    print(f"总计检测到 {len(landmarks_data)} 帧有人体姿态", file=sys.stderr)
    
    return landmarks_data


def main():
    if len(sys.argv) < 2:
        print("用法: python pose_analyzer.py <视频文件路径>", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    print(f"正在分析视频: {video_path}", file=sys.stderr)
    print("正在提取姿态关键点...", file=sys.stderr)
    
    landmarks = extract_pose(video_path)
    
    if landmarks:
        print(f"\n成功提取 {len(landmarks)} 帧姿态数据", file=sys.stderr)
        print("\n=== POSE_DATA_START ===", file=sys.stderr)
        print(json.dumps(landmarks, ensure_ascii=False), file=sys.stderr)
        print("=== POSE_DATA_END ===", file=sys.stderr)
        
        # 输出 JSON 格式供 agent 读取
        result = {
            "status": "success",
            "frames_analyzed": len(landmarks),
            "pose_data": landmarks
        }
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("错误: 未能提取到姿态数据", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
