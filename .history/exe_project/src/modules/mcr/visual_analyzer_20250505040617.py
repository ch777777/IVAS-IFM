"""
视觉分析器
负责分析视频画面内容，识别物体、场景和视觉属性
"""
import os
import logging
import tempfile
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
import torch

try:
    from ultralytics import YOLO
    from transformers import CLIPProcessor, CLIPModel
except ImportError:
    raise ImportError("请安装必要的依赖: pip install ultralytics transformers torch")

logger = logging.getLogger(__name__)

class VisualAnalyzer:
    """视觉分析器，负责视频画面分析"""
    
    def __init__(self, 
                 yolo_model: str = 'yolov8n.pt',
                 clip_model: str = 'openai/clip-vit-base-patch32',
                 device: str = None,
                 conf_threshold: float = 0.25):
        """
        初始化视觉分析器
        
        Args:
            yolo_model: YOLOv8模型路径或名称
            clip_model: CLIP模型名称
            device: 计算设备 ('cuda' 或 'cpu')
            conf_threshold: 目标检测置信度阈值
        """
        self.conf_threshold = conf_threshold
        
        # 自动选择设备
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        # 加载YOLO模型
        try:
            self.yolo = YOLO(yolo_model)
            logger.info(f"成功加载YOLO模型: {yolo_model}")
        except Exception as e:
            logger.error(f"加载YOLO模型失败: {str(e)}")
            self.yolo = None
            
        # 加载CLIP模型
        try:
            self.clip_processor = CLIPProcessor.from_pretrained(clip_model)
            self.clip_model = CLIPModel.from_pretrained(clip_model).to(self.device)
            logger.info(f"成功加载CLIP模型: {clip_model}")
        except Exception as e:
            logger.error(f"加载CLIP模型失败: {str(e)}")
            self.clip_processor = None
            self.clip_model = None
            
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析单张图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            分析结果字典
        """
        results = {
            'objects': [],
            'scene_attributes': [],
            'visual_concepts': [],
            'image_attributes': {}
        }
        
        # 加载图像
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"无法读取图像: {image_path}")
            return results
            
        # BGR转RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 检测物体
        if self.yolo:
            object_results = self.detect_objects(image_rgb)
            results['objects'] = object_results
            
        # 分析图像属性
        results['image_attributes'] = self.analyze_image_attributes(image)
        
        # 识别视觉概念
        if self.clip_model and self.clip_processor:
            # 预定义的视觉概念和场景属性
            visual_concepts = [
                "户外场景", "室内场景", "城市", "自然风光", "人物特写", 
                "产品展示", "科技", "体育运动", "美食", "时尚", 
                "动物", "植物", "建筑", "夜景", "天空",
                "水体", "山脉", "沙漠", "森林", "雪景"
            ]
            
            scene_attributes = [
                "明亮的", "黑暗的", "多彩的", "单色的", "繁忙的", 
                "平静的", "现代的", "复古的", "豪华的", "简约的",
                "杂乱的", "整洁的", "温暖的", "冷色调的", "模糊的",
                "清晰的", "动态的", "静态的", "密集的", "稀疏的"
            ]
            
            # 获取图像-文本匹配分数
            concept_scores = self.match_visual_concepts(image_rgb, visual_concepts)
            attribute_scores = self.match_visual_concepts(image_rgb, scene_attributes)
            
            # 过滤得分高的概念和属性
            results['visual_concepts'] = [
                {'concept': concept, 'score': float(score)}
                for concept, score in concept_scores
                if score > 0.25  # 设置阈值
            ]
            
            results['scene_attributes'] = [
                {'attribute': attr, 'score': float(score)}
                for attr, score in attribute_scores
                if score > 0.25  # 设置阈值
            ]
            
        return results
        
    def analyze_video(self, 
                      video_path: str, 
                      sample_rate: int = 1,
                      max_frames: int = 10) -> Dict:
        """
        分析视频内容
        
        Args:
            video_path: 视频文件路径
            sample_rate: 采样率，每隔多少帧取一帧
            max_frames: 最大处理帧数
            
        Returns:
            分析结果字典
        """
        results = {
            'frames': [],
            'objects': {},
            'scene_changes': [],
            'dominant_scenes': [],
            'summary': {}
        }
        
        # 打开视频文件
        try:
            cap = cv2.VideoCapture(video_path)
            
            # 获取视频基本信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            results['summary'] = {
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'width': width,
                'height': height,
                'sampled_frames': 0
            }
            
            # 临时目录保存帧
            with tempfile.TemporaryDirectory() as temp_dir:
                frame_index = 0
                sampled_count = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret or sampled_count >= max_frames:
                        break
                        
                    # 按采样率提取帧
                    if frame_index % sample_rate == 0:
                        # 保存帧为临时图像
                        frame_path = os.path.join(temp_dir, f"frame_{sampled_count}.jpg")
                        cv2.imwrite(frame_path, frame)
                        
                        # 分析该帧
                        frame_result = self.analyze_image(frame_path)
                        frame_result['frame_index'] = frame_index
                        frame_result['timestamp'] = frame_index / fps if fps > 0 else 0
                        
                        results['frames'].append(frame_result)
                        sampled_count += 1
                        
                    frame_index += 1
                    
                results['summary']['sampled_frames'] = sampled_count
                
            # 关闭视频文件
            cap.release()
            
            # 汇总物体检测结果
            all_objects = {}
            for frame in results['frames']:
                for obj in frame['objects']:
                    obj_name = obj['name']
                    if obj_name not in all_objects:
                        all_objects[obj_name] = {
                            'count': 0,
                            'first_appearance': frame['timestamp'],
                            'appearances': []
                        }
                    
                    all_objects[obj_name]['count'] += 1
                    all_objects[obj_name]['appearances'].append({
                        'timestamp': frame['timestamp'],
                        'confidence': obj['confidence'],
                        'box': obj['box']
                    })
            
            # 按出现次数排序
            results['objects'] = {
                name: info for name, info in 
                sorted(all_objects.items(), key=lambda x: x[1]['count'], reverse=True)
            }
            
            # 识别场景变化
            if len(results['frames']) > 1:
                results['scene_changes'] = self.detect_scene_changes(results['frames'])
                
            # 获取主要场景
            results['dominant_scenes'] = self.extract_dominant_scenes(results['frames'])
            
            return results
            
        except Exception as e:
            logger.error(f"视频分析失败: {str(e)}")
            return results
        
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        检测图像中的物体
        
        Args:
            image: 图像数组(RGB格式)
            
        Returns:
            检测到的物体列表
        """
        if self.yolo is None:
            return []
            
        try:
            # 使用YOLOv8检测物体
            detections = self.yolo(image, conf=self.conf_threshold)[0]
            results = []
            
            # 处理检测结果
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, confidence, class_id = detection
                
                class_name = detections.names[int(class_id)]
                
                results.append({
                    'name': class_name,
                    'confidence': float(confidence),
                    'box': [float(x1), float(y1), float(x2), float(y2)]
                })
                
            return results
            
        except Exception as e:
            logger.error(f"物体检测失败: {str(e)}")
            return []
            
    def analyze_image_attributes(self, image: np.ndarray) -> Dict:
        """
        分析图像属性(亮度、对比度、颜色分布等)
        
        Args:
            image: 图像数组(BGR格式)
            
        Returns:
            图像属性字典
        """
        try:
            # 转为灰度图计算亮度和对比度
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 亮度: 平均像素值
            brightness = np.mean(gray)
            
            # 对比度: 标准差
            contrast = np.std(gray)
            
            # 颜色分布: 各通道平均值
            b, g, r = cv2.split(image)
            color_distribution = {
                'red': float(np.mean(r)),
                'green': float(np.mean(g)),
                'blue': float(np.mean(b))
            }
            
            # 颜色分布直方图
            color_hist = {}
            for i, channel in enumerate(['blue', 'green', 'red']):
                hist = cv2.calcHist([image], [i], None, [8], [0, 256])
                color_hist[channel] = [float(x[0]) for x in hist]
                
            # 锐度: 拉普拉斯算子的方差
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # 纹理特征: Haralick纹理
            # 需要安装mahotas库才能使用下面的功能
            # import mahotas
            # textures = mahotas.features.haralick(gray).mean(axis=0)
            # texture_features = {f"texture_{i}": float(x) for i, x in enumerate(textures)}
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'sharpness': float(sharpness),
                'color_distribution': color_distribution,
                'color_histogram': color_hist,
                'resolution': [image.shape[1], image.shape[0]]  # 宽x高
            }
            
        except Exception as e:
            logger.error(f"图像属性分析失败: {str(e)}")
            return {}
            
    def match_visual_concepts(self, 
                             image: np.ndarray, 
                             concepts: List[str]) -> List[Tuple[str, float]]:
        """
        将图像与视觉概念进行匹配
        
        Args:
            image: 图像数组(RGB格式)
            concepts: 待匹配的视觉概念列表
            
        Returns:
            匹配结果，按得分降序排列
        """
        if self.clip_model is None or self.clip_processor is None:
            return []
            
        try:
            # 准备图像
            inputs = self.clip_processor(
                text=concepts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # 获取图像-文本相似度
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]
                
            # 返回概念和对应的概率
            results = list(zip(concepts, probs))
            
            # 按概率降序排列
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"视觉概念匹配失败: {str(e)}")
            return []
            
    def detect_scene_changes(self, frames: List[Dict]) -> List[Dict]:
        """
        检测视频中的场景变化
        
        Args:
            frames: 帧分析结果列表
            
        Returns:
            场景变化列表
        """
        scene_changes = []
        prev_concepts = set()
        
        for i, frame in enumerate(frames):
            # 提取主要视觉概念
            current_concepts = set(item['concept'] for item in frame['visual_concepts'][:3])
            
            # 第一帧或与前一帧概念差异大
            if i == 0 or len(current_concepts.symmetric_difference(prev_concepts)) > 1:
                scene_changes.append({
                    'timestamp': frame['timestamp'],
                    'frame_index': frame['frame_index'],
                    'concepts': list(current_concepts)
                })
                
            prev_concepts = current_concepts
            
        return scene_changes
        
    def extract_dominant_scenes(self, frames: List[Dict]) -> List[Dict]:
        """
        提取视频主要场景
        
        Args:
            frames: 帧分析结果列表
            
        Returns:
            主要场景列表
        """
        # 统计概念出现频率
        concept_counts = {}
        for frame in frames:
            for item in frame['visual_concepts']:
                concept = item['concept']
                if concept not in concept_counts:
                    concept_counts[concept] = 0
                concept_counts[concept] += 1
                
        # 选择出现频率最高的N个概念
        dominant_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 转换为所需格式
        return [
            {'concept': concept, 'frequency': count / len(frames)}
            for concept, count in dominant_concepts
        ]


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建视觉分析器
    analyzer = VisualAnalyzer()
    
    # 测试图像分析
    image_path = "sample_image.jpg"
    if os.path.exists(image_path):
        print(f"分析图像: {image_path}")
        results = analyzer.analyze_image(image_path)
        
        print(f"检测到 {len(results['objects'])} 个物体:")
        for obj in results['objects']:
            print(f"  - {obj['name']}: {obj['confidence']:.2f}")
            
        print("\n视觉概念:")
        for concept in results['visual_concepts'][:5]:
            print(f"  - {concept['concept']}: {concept['score']:.2f}")
            
        print("\n场景属性:")
        for attr in results['scene_attributes'][:5]:
            print(f"  - {attr['attribute']}: {attr['score']:.2f}")
    
    # 测试视频分析
    video_path = "sample_video.mp4"
    if os.path.exists(video_path):
        print(f"\n分析视频: {video_path}")
        video_results = analyzer.analyze_video(video_path, sample_rate=30, max_frames=5)
        
        print(f"分析了 {video_results['summary']['sampled_frames']} 帧")
        print("\n主要物体:")
        for obj_name, obj_info in list(video_results['objects'].items())[:3]:
            print(f"  - {obj_name}: 出现 {obj_info['count']} 次")
            
        print("\n主要场景:")
        for scene in video_results['dominant_scenes']:
            print(f"  - {scene['concept']}: 频率 {scene['frequency']:.2f}") 