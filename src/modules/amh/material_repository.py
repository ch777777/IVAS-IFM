"""
素材仓库模块
负责结构化存储和管理广告素材
"""
import os
import json
import shutil
import logging
import datetime
import uuid
from typing import List, Dict, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class MaterialRepository:
    """素材仓库，负责管理广告素材的存储和检索"""
    
    def __init__(self, base_dir: str):
        """
        初始化素材仓库
        
        Args:
            base_dir: 素材存储的基础目录
        """
        self.base_dir = base_dir
        
        # 创建必要的目录结构
        self._create_directory_structure()
        
        # 加载素材索引
        self.index = self._load_index()
        
    def _create_directory_structure(self):
        """创建素材库的目录结构"""
        try:
            # 创建主目录
            os.makedirs(self.base_dir, exist_ok=True)
            
            # 创建子目录
            subdirs = [
                'videos',       # 原始视频
                'images',       # 图像素材
                'audio',        # 音频素材
                'segments',     # 视频片段
                'exports',      # 导出作品
                'temp',         # 临时文件
                'metadata'      # 元数据文件
            ]
            
            for subdir in subdirs:
                os.makedirs(os.path.join(self.base_dir, subdir), exist_ok=True)
                
            logger.info(f"创建素材库目录结构: {self.base_dir}")
            return True
            
        except Exception as e:
            logger.error(f"创建目录结构失败: {str(e)}")
            raise
            
    def _get_index_path(self) -> str:
        """获取索引文件路径"""
        return os.path.join(self.base_dir, 'metadata', 'material_index.json')
        
    def _load_index(self) -> Dict:
        """加载素材索引"""
        index_path = self._get_index_path()
        
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载素材索引失败: {str(e)}")
                # 返回新索引
                return self._create_new_index()
        else:
            return self._create_new_index()
            
    def _create_new_index(self) -> Dict:
        """创建新的素材索引"""
        index = {
            'version': '1.0',
            'created_at': datetime.datetime.now().isoformat(),
            'last_updated': datetime.datetime.now().isoformat(),
            'total_materials': 0,
            'categories': {},
            'materials': {}
        }
        
        # 保存新索引
        self._save_index(index)
        
        return index
        
    def _save_index(self, index: Dict = None) -> bool:
        """保存素材索引"""
        if index is None:
            index = self.index
            
        # 更新时间戳
        index['last_updated'] = datetime.datetime.now().isoformat()
        
        try:
            index_path = self._get_index_path()
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存素材索引失败: {str(e)}")
            return False
            
    def add_material(self, 
                    file_path: str, 
                    material_type: str, 
                    metadata: Dict,
                    tags: List[str] = None,
                    category: str = None,
                    move_file: bool = True) -> str:
        """
        添加素材到仓库
        
        Args:
            file_path: 素材文件路径
            material_type: 素材类型('video', 'segment', 'image', 'audio')
            metadata: 素材元数据
            tags: 素材标签
            category: 素材分类
            move_file: 是否移动文件(True为移动，False为复制)
            
        Returns:
            素材ID
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"素材文件不存在: {file_path}")
            
        # 生成唯一ID
        material_id = str(uuid.uuid4())
        
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        
        # 确定目标目录
        if material_type == 'video':
            target_dir = os.path.join(self.base_dir, 'videos')
        elif material_type == 'segment':
            target_dir = os.path.join(self.base_dir, 'segments')
        elif material_type == 'image':
            target_dir = os.path.join(self.base_dir, 'images')
        elif material_type == 'audio':
            target_dir = os.path.join(self.base_dir, 'audio')
        else:
            raise ValueError(f"不支持的素材类型: {material_type}")
            
        # 生成目标文件路径
        target_path = os.path.join(target_dir, f"{material_id}{ext}")
        
        # 复制或移动文件
        try:
            if move_file:
                shutil.move(file_path, target_path)
            else:
                shutil.copy2(file_path, target_path)
        except Exception as e:
            logger.error(f"复制/移动文件失败: {str(e)}")
            raise
            
        # 准备素材信息
        now = datetime.datetime.now().isoformat()
        material_info = {
            'id': material_id,
            'type': material_type,
            'file_path': target_path,
            'original_filename': os.path.basename(file_path),
            'added_at': now,
            'last_accessed': now,
            'metadata': metadata,
            'tags': tags or [],
            'category': category,
            'related_materials': []
        }
        
        # 更新索引
        self.index['materials'][material_id] = material_info
        self.index['total_materials'] += 1
        
        # 更新分类
        if category:
            if category not in self.index['categories']:
                self.index['categories'][category] = {
                    'count': 0,
                    'materials': []
                }
            self.index['categories'][category]['count'] += 1
            self.index['categories'][category]['materials'].append(material_id)
            
        # 保存索引
        self._save_index()
        
        logger.info(f"添加素材成功: {material_id}, 类型: {material_type}")
        
        return material_id
        
    def get_material(self, material_id: str) -> Optional[Dict]:
        """
        获取素材信息
        
        Args:
            material_id: 素材ID
            
        Returns:
            素材信息字典，如果不存在则返回None
        """
        if material_id in self.index['materials']:
            # 更新访问时间
            self.index['materials'][material_id]['last_accessed'] = datetime.datetime.now().isoformat()
            self._save_index()
            
            return self.index['materials'][material_id]
        else:
            logger.warning(f"素材不存在: {material_id}")
            return None
            
    def get_material_path(self, material_id: str) -> Optional[str]:
        """
        获取素材文件路径
        
        Args:
            material_id: 素材ID
            
        Returns:
            素材文件路径，如果不存在则返回None
        """
        material = self.get_material(material_id)
        if material:
            return material['file_path']
        return None
        
    def update_material_metadata(self, 
                               material_id: str, 
                               metadata: Dict,
                               merge: bool = True) -> bool:
        """
        更新素材元数据
        
        Args:
            material_id: 素材ID
            metadata: 新的元数据
            merge: 是否合并现有元数据
            
        Returns:
            更新是否成功
        """
        if material_id not in self.index['materials']:
            logger.warning(f"素材不存在: {material_id}")
            return False
            
        try:
            if merge:
                # 合并元数据
                current_metadata = self.index['materials'][material_id]['metadata']
                current_metadata.update(metadata)
            else:
                # 替换元数据
                self.index['materials'][material_id]['metadata'] = metadata
                
            # 更新修改时间
            self.index['materials'][material_id]['last_accessed'] = datetime.datetime.now().isoformat()
            
            # 保存索引
            self._save_index()
            
            logger.info(f"更新素材元数据成功: {material_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新素材元数据失败: {str(e)}")
            return False
            
    def update_material_tags(self, 
                           material_id: str, 
                           tags: List[str],
                           replace: bool = False) -> bool:
        """
        更新素材标签
        
        Args:
            material_id: 素材ID
            tags: 标签列表
            replace: 是否替换现有标签
            
        Returns:
            更新是否成功
        """
        if material_id not in self.index['materials']:
            logger.warning(f"素材不存在: {material_id}")
            return False
            
        try:
            if replace:
                self.index['materials'][material_id]['tags'] = tags
            else:
                # 合并标签并去重
                current_tags = set(self.index['materials'][material_id]['tags'])
                current_tags.update(tags)
                self.index['materials'][material_id]['tags'] = list(current_tags)
                
            # 更新修改时间
            self.index['materials'][material_id]['last_accessed'] = datetime.datetime.now().isoformat()
            
            # 保存索引
            self._save_index()
            
            logger.info(f"更新素材标签成功: {material_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新素材标签失败: {str(e)}")
            return False
            
    def delete_material(self, material_id: str, delete_file: bool = True) -> bool:
        """
        删除素材
        
        Args:
            material_id: 素材ID
            delete_file: 是否删除文件
            
        Returns:
            删除是否成功
        """
        if material_id not in self.index['materials']:
            logger.warning(f"素材不存在: {material_id}")
            return False
            
        try:
            material = self.index['materials'][material_id]
            
            # 删除文件
            if delete_file and os.path.exists(material['file_path']):
                os.remove(material['file_path'])
                
            # 更新分类
            category = material.get('category')
            if category and category in self.index['categories']:
                if material_id in self.index['categories'][category]['materials']:
                    self.index['categories'][category]['materials'].remove(material_id)
                self.index['categories'][category]['count'] -= 1
                
                # 如果分类为空，考虑删除它
                if self.index['categories'][category]['count'] <= 0:
                    del self.index['categories'][category]
            
            # 从索引中删除
            del self.index['materials'][material_id]
            self.index['total_materials'] -= 1
            
            # 保存索引
            self._save_index()
            
            logger.info(f"删除素材成功: {material_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除素材失败: {str(e)}")
            return False
            
    def search_materials(self, 
                        query: str = None, 
                        material_type: str = None,
                        tags: List[str] = None,
                        category: str = None,
                        metadata_filters: Dict = None,
                        limit: int = 100,
                        offset: int = 0) -> Tuple[List[Dict], int]:
        """
        搜索素材
        
        Args:
            query: 搜索关键词
            material_type: 素材类型
            tags: 标签列表(与关系)
            category: 分类
            metadata_filters: 元数据过滤条件
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            匹配的素材列表和总数量
        """
        results = []
        
        # 首先按分类过滤
        if category and category in self.index['categories']:
            # 获取分类中的所有素材ID
            material_ids = self.index['categories'][category]['materials']
            candidates = {mid: self.index['materials'][mid] for mid in material_ids if mid in self.index['materials']}
        else:
            # 使用所有素材
            candidates = self.index['materials']
            
        # 按照条件过滤
        for material_id, material in candidates.items():
            # 按类型过滤
            if material_type and material['type'] != material_type:
                continue
                
            # 按标签过滤(必须包含所有指定标签)
            if tags:
                material_tags = set(material['tags'])
                if not all(tag in material_tags for tag in tags):
                    continue
                    
            # 按元数据过滤
            if metadata_filters:
                material_metadata = material['metadata']
                match = True
                
                for key, value in metadata_filters.items():
                    # 嵌套键名处理 (例如 "video.duration")
                    if '.' in key:
                        parts = key.split('.')
                        curr = material_metadata
                        for part in parts[:-1]:
                            if part not in curr:
                                match = False
                                break
                            curr = curr[part]
                        
                        if not match or parts[-1] not in curr or curr[parts[-1]] != value:
                            match = False
                    else:
                        if key not in material_metadata or material_metadata[key] != value:
                            match = False
                            
                if not match:
                    continue
                    
            # 关键词搜索
            if query:
                query_lower = query.lower()
                
                # 搜索原始文件名
                if query_lower in material['original_filename'].lower():
                    results.append(material)
                    continue
                    
                # 搜索标签
                found_in_tags = False
                for tag in material['tags']:
                    if query_lower in tag.lower():
                        found_in_tags = True
                        break
                        
                if found_in_tags:
                    results.append(material)
                    continue
                    
                # 搜索元数据的值
                found_in_metadata = False
                for k, v in material['metadata'].items():
                    if isinstance(v, str) and query_lower in v.lower():
                        found_in_metadata = True
                        break
                        
                if found_in_metadata:
                    results.append(material)
                    continue
            else:
                # 没有查询关键词，添加到结果
                results.append(material)
                
        # 按最后访问时间排序(最近访问的排在前面)
        results.sort(key=lambda x: x['last_accessed'], reverse=True)
        
        # 应用分页
        total_count = len(results)
        results = results[offset:offset+limit]
        
        return results, total_count
        
    def create_category(self, category_name: str, description: str = None) -> bool:
        """
        创建素材分类
        
        Args:
            category_name: 分类名称
            description: 分类描述
            
        Returns:
            创建是否成功
        """
        if category_name in self.index['categories']:
            logger.warning(f"分类已存在: {category_name}")
            return False
            
        self.index['categories'][category_name] = {
            'count': 0,
            'materials': [],
            'description': description,
            'created_at': datetime.datetime.now().isoformat()
        }
        
        # 保存索引
        self._save_index()
        
        logger.info(f"创建分类成功: {category_name}")
        return True
        
    def get_all_categories(self) -> Dict:
        """
        获取所有分类
        
        Returns:
            分类字典
        """
        return self.index['categories']
        
    def set_material_category(self, material_id: str, category: str) -> bool:
        """
        设置素材分类
        
        Args:
            material_id: 素材ID
            category: 分类名称
            
        Returns:
            设置是否成功
        """
        if material_id not in self.index['materials']:
            logger.warning(f"素材不存在: {material_id}")
            return False
            
        # 获取当前分类
        current_category = self.index['materials'][material_id].get('category')
        
        # 如果分类相同，不做任何操作
        if current_category == category:
            return True
            
        # 从当前分类移除
        if current_category and current_category in self.index['categories']:
            if material_id in self.index['categories'][current_category]['materials']:
                self.index['categories'][current_category]['materials'].remove(material_id)
            self.index['categories'][current_category]['count'] -= 1
            
        # 添加到新分类
        if category:
            # 如果分类不存在，创建它
            if category not in self.index['categories']:
                self.create_category(category)
                
            self.index['categories'][category]['materials'].append(material_id)
            self.index['categories'][category]['count'] += 1
            
        # 更新素材信息
        self.index['materials'][material_id]['category'] = category
        
        # 保存索引
        self._save_index()
        
        logger.info(f"设置素材分类成功: {material_id} -> {category}")
        return True
        
    def link_materials(self, source_id: str, target_id: str, relation_type: str = 'related') -> bool:
        """
        关联两个素材
        
        Args:
            source_id: 源素材ID
            target_id: 目标素材ID
            relation_type: 关系类型
            
        Returns:
            关联是否成功
        """
        if source_id not in self.index['materials']:
            logger.warning(f"源素材不存在: {source_id}")
            return False
            
        if target_id not in self.index['materials']:
            logger.warning(f"目标素材不存在: {target_id}")
            return False
            
        # 检查是否已关联
        for relation in self.index['materials'][source_id].get('related_materials', []):
            if relation.get('id') == target_id:
                # 更新关系类型
                relation['type'] = relation_type
                self._save_index()
                return True
                
        # 添加关联
        if 'related_materials' not in self.index['materials'][source_id]:
            self.index['materials'][source_id]['related_materials'] = []
            
        self.index['materials'][source_id]['related_materials'].append({
            'id': target_id,
            'type': relation_type,
            'linked_at': datetime.datetime.now().isoformat()
        })
        
        # 保存索引
        self._save_index()
        
        logger.info(f"关联素材成功: {source_id} -> {target_id} ({relation_type})")
        return True
        
    def get_statistics(self) -> Dict:
        """
        获取素材库统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_materials': self.index['total_materials'],
            'total_categories': len(self.index['categories']),
            'type_counts': {},
            'top_tags': {},
            'recent_materials': []
        }
        
        # 统计各类型素材数量
        for material in self.index['materials'].values():
            material_type = material['type']
            if material_type not in stats['type_counts']:
                stats['type_counts'][material_type] = 0
            stats['type_counts'][material_type] += 1
            
            # 统计标签
            for tag in material['tags']:
                if tag not in stats['top_tags']:
                    stats['top_tags'][tag] = 0
                stats['top_tags'][tag] += 1
                
        # 获取最近添加的素材
        recent_materials = sorted(
            self.index['materials'].values(),
            key=lambda x: x['added_at'],
            reverse=True
        )[:10]
        
        stats['recent_materials'] = [
            {
                'id': material['id'],
                'type': material['type'],
                'original_filename': material['original_filename'],
                'added_at': material['added_at']
            }
            for material in recent_materials
        ]
        
        # 限制标签数量
        stats['top_tags'] = dict(sorted(
            stats['top_tags'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20])
        
        return stats
        
    def export_index(self, output_path: str = None) -> str:
        """
        导出素材索引
        
        Args:
            output_path: 输出文件路径，默认为metadata目录下的时间戳文件
            
        Returns:
            导出文件路径
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.base_dir,
                'metadata',
                f'material_index_export_{timestamp}.json'
            )
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
                
            logger.info(f"导出素材索引成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"导出素材索引失败: {str(e)}")
            raise
            
    def import_index(self, input_path: str, merge: bool = False) -> bool:
        """
        导入素材索引
        
        Args:
            input_path: 输入文件路径
            merge: 是否合并到现有索引
            
        Returns:
            导入是否成功
        """
        if not os.path.exists(input_path):
            logger.error(f"索引文件不存在: {input_path}")
            return False
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                new_index = json.load(f)
                
            if merge:
                # 合并素材
                for material_id, material in new_index['materials'].items():
                    if material_id not in self.index['materials']:
                        self.index['materials'][material_id] = material
                        
                # 合并分类
                for category, info in new_index['categories'].items():
                    if category not in self.index['categories']:
                        self.index['categories'][category] = info
                    else:
                        # 合并素材列表
                        materials_set = set(self.index['categories'][category]['materials'])
                        materials_set.update(info['materials'])
                        self.index['categories'][category]['materials'] = list(materials_set)
                        self.index['categories'][category]['count'] = len(materials_set)
                        
                # 更新总数量
                self.index['total_materials'] = len(self.index['materials'])
                
            else:
                # 替换整个索引
                self.index = new_index
                
            # 保存索引
            self._save_index()
            
            logger.info(f"导入素材索引成功: {input_path}")
            return True
            
        except Exception as e:
            logger.error(f"导入素材索引失败: {str(e)}")
            return False


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建素材仓库
    repo_dir = os.path.join(os.getcwd(), "material_repository")
    repo = MaterialRepository(repo_dir)
    
    # 创建分类
    repo.create_category("产品特写", "产品细节展示的特写镜头")
    repo.create_category("用户评价", "用户实际使用产品并评价的视频")
    repo.create_category("产品使用", "产品使用场景和方法展示")
    
    print("\n当前素材库分类:")
    for category, info in repo.get_all_categories().items():
        print(f"  - {category}: {info['count']}个素材")
    
    # 添加测试素材(如果有测试文件)
    test_video = "sample_video.mp4"
    if os.path.exists(test_video):
        # 添加视频素材
        material_id = repo.add_material(
            file_path=test_video,
            material_type='video',
            metadata={
                'duration': 120,  # 秒
                'resolution': '1920x1080',
                'source': 'demo'
            },
            tags=["演示", "测试视频", "样例"],
            category="产品特写",
            move_file=False  # 复制而不是移动
        )
        
        print(f"\n添加测试素材: {material_id}")
        
        # 查询素材
        material = repo.get_material(material_id)
        if material:
            print(f"素材信息:")
            print(f"  - 类型: {material['type']}")
            print(f"  - 文件名: {material['original_filename']}")
            print(f"  - 标签: {', '.join(material['tags'])}")
            
    # 搜索素材
    results, count = repo.search_materials(
        material_type='video',
        tags=["测试视频"],
        limit=5
    )
    
    print(f"\n搜索结果: 找到 {count} 个素材")
    for material in results:
        print(f"  - {material['id']}: {material['original_filename']}")
        
    # 获取统计信息
    stats = repo.get_statistics()
    print("\n素材库统计:")
    print(f"  - 总素材数: {stats['total_materials']}")
    print(f"  - 分类数: {stats['total_categories']}")
    print(f"  - 素材类型分布: {stats['type_counts']}")
    print(f"  - 最常用标签: {list(stats['top_tags'].keys())[:5]}") 
 
 