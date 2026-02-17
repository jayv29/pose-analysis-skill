#!/usr/bin/env python3
"""
Pose Analysis Script - Enhanced
用 MediaPipe 分析训练视频姿态，输出生物力学角度和关键帧
"""

import sys
import json
import os
import math
from pathlib import Path
from typing import List, Dict, Tuple

# 虚拟环境路径
VENV_PATH = Path.home() / ".venv-pose"


class GeometryUtils:
    @staticmethod
    def calculate_angle(a: Dict, b: Dict, c: Dict) -> float:
        """
        计算三点之间的角度 (0-180度)
        a: 第一个点 (如 Hip)
        b: 中间点 (如 Knee)
        c: 第三个点 (如 Ankle)
        """
        # 转换为向量
        ba = [a['x'] - b['x'], a['y'] - b['y']]
        bc = [c['x'] - b['x'], c['y'] - b['y']]
        
        # 计算向量长度
        norm_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        norm_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        
        if norm_ba == 0 or norm_bc == 0:
            return 0.0
            
        # 计算点积
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        
        # 计算角度 (弧度 -> 角度)
        try:
            angle = math.degrees(math.acos(dot_product / (norm_ba * norm_bc)))
        except ValueError:
            return 0.0 # 处理浮点误差导致的 domain error
            
        return round(angle, 1)

    @staticmethod
    def get_landmark(landmarks: List[Dict], index: int) -> Dict:
        """安全获取关键点"""
        if index < len(landmarks):
            return landmarks[index]
        return {'x': 0, 'y': 0, 'z': 0, 'visibility': 0}


def analyze_frame_metrics(landmarks: List[Dict]) -> Dict:
    """计算单帧的生物力学指标"""
    utils = GeometryUtils()
    
    # MediaPipe Pose Landmarks 索引:
    # 11: left_shoulder, 12: right_shoulder
    # 23: left_hip,      24: right_hip
    # 25: left_knee,     26: right_knee
    # 27: left_ankle,    28: right_ankle
    
    # 获取关键点
    l_hip = utils.get_landmark(landmarks, 23)
    l_knee = utils.get_landmark(landmarks, 25)
    l_ankle = utils.get_landmark(landmarks, 27)
    
    r_hip = utils.get_landmark(landmarks, 24)
    r_knee = utils.get_landmark(landmarks, 26)
    r_ankle = utils.get_landmark(landmarks, 28)
    
    metrics = {
        "knee_angle_left": utils.calculate_angle(l_hip, l_knee, l_ankle),
        "knee_angle_right": utils.calculate_angle(r_hip, r_knee, r_ankle),
        # 可以添加更多指标...
        "hip_height": round((l_hip['y'] + r_hip['y']) / 2, 3) # y 越大越低 (0在上, 1在下)
    }
    
    return metrics


def extract_pose(video_path: str) -> dict:
    """用 MediaPipe 提取姿态关键点并计算指标"""
    # 延迟导入以加快启动速度
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        import mediapipe as mp
        import cv2
    except ImportError:
        print("错误: 缺少依赖库。请运行 pip install mediapipe opencv-python", file=sys.stderr)
        sys.exit(1)
    
    print(f"正在处理视频: {video_path}", file=sys.stderr)
    
    # 配置 PoseLandmarker
    # 注意: 模型路径可能需要根据实际安装位置调整
    model_path = '/tmp/pose_landmarker.task'
    if not os.path.exists(model_path):
        print(f"警告: 模型文件不存在于 {model_path}，尝试自动下载...", file=sys.stderr)
        # 这里可以加入自动下载逻辑，暂时略过
    
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1
    )
    
    try:
        detector = vision.PoseLandmarker.create_from_options(options)
    except Exception as e:
        print(f"错误: 加载模型失败 - {e}", file=sys.stderr)
        return {}
    
    # 读取视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频 {video_path}", file=sys.stderr)
        return {}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    analyzed_frames = []
    
    # 用于关键帧检测的变量
    min_hip_y = 0 # 记录最低重心 (y值最大)
    lowest_cg_frame = None
    
    print(f"视频 FPS: {fps}", file=sys.stderr)
    
    while cap.isOpened() and frame_count < 450:  # 增加限制到 450 帧 (约15秒)
        success, image = cap.read()
        if not success:
            break
        
        # 采样率: 每 5 帧分析一次 (约 6fps)，以捕捉更多细节
        if frame_count % 5 == 0:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # 检测姿态
            timestamp_ms = int(frame_count * 1000 / fps)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                raw_landmarks = []
                # 转换 landmarks 格式
                for lm in result.pose_landmarks[0]:
                    raw_landmarks.append({
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z if hasattr(lm, 'z') else 0
                    })
                
                # 计算生物力学指标
                metrics = analyze_frame_metrics(raw_landmarks)
                
                frame_data = {
                    "frame": frame_count,
                    "timestamp": round(timestamp_ms / 1000, 2),
                    "metrics": metrics,
                    # 仅保留关键的 raw landmarks 以减小 tokens (如需要)
                    # "landmarks": raw_landmarks 
                }
                analyzed_frames.append(frame_data)
                
                # 简单的关键帧检测逻辑: 寻找重心最低点 (Lunge visual)
                if metrics['hip_height'] > min_hip_y:
                    min_hip_y = metrics['hip_height']
                    lowest_cg_frame = frame_data
                
            else:
                pass # 未检测到
        
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"已处理 {frame_count} 帧...", file=sys.stderr)
    
    cap.release()
    print(f"总计分析 {len(analyzed_frames)} 帧", file=sys.stderr)
    
    return {
        "all_frames": analyzed_frames,
        "key_frames": {
            "lowest_center_of_gravity": lowest_cg_frame
        }
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python pose_analyzer.py <视频文件路径>", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    print(f"正在分析视频: {video_path}", file=sys.stderr)
    print("正在提取姿态关键点并计算生物力学指标...", file=sys.stderr)
    
    result_data = extract_pose(video_path)
    
    if result_data and result_data["all_frames"]:
        print(f"\n成功提取数据", file=sys.stderr)
        print("\n=== POSE_DATA_START ===", file=sys.stderr)
        # 精简输出: 只输出关键帧和少量采样帧给 LLM，防止 token 爆炸
        final_output = {
            "summary": {
                "total_frames": len(result_data["all_frames"]),
                "duration_sec": result_data["all_frames"][-1]["timestamp"]
            },
            "key_frames": result_data["key_frames"],
            # 可以在这里添加更多逻辑，比如每秒取一个样本
            "sampled_frames": result_data["all_frames"][::6] # 再次降采样，确保 token 数量可控
        }
        print(json.dumps(final_output, ensure_ascii=False), file=sys.stderr)
        print("=== POSE_DATA_END ===", file=sys.stderr)
        
        # 标准输出给 OpenClaw
        print(json.dumps(final_output, ensure_ascii=False))
    else:
        print("错误: 未能提取到有效姿态数据", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
