"""
关键词提取器
负责从文本内容中提取关键词和主题
"""
import logging
import re
from typing import List, Dict, Tuple, Any, Optional, Union
from collections import Counter
import string
import math

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    import jieba
    import jieba.analyse
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except ImportError:
    raise ImportError("请安装必要的依赖: pip install transformers jieba nltk")

logger = logging.getLogger(__name__)

class KeywordGenerator:
    """关键词提取器，从文本中提取关键词和主题"""
    
    def __init__(self, 
                language: str = 'auto',
                max_keywords: int = 10,
                use_transformers: bool = True,
                chinese_model: str = None,
                english_model: str = None):
        """
        初始化关键词提取器
        
        Args:
            language: 语言选项 ('chinese', 'english', 'auto')
            max_keywords: 每次提取的最大关键词数量
            use_transformers: 是否使用Transformers模型
            chinese_model: 中文关键词提取模型
            english_model: 英文关键词提取模型
        """
        self.language = language
        self.max_keywords = max_keywords
        self.use_transformers = use_transformers
        
        # 加载停用词
        self.stop_words = {
            'chinese': self._load_chinese_stopwords(),
            'english': set(stopwords.words('english')) if 'stopwords' in nltk.__dict__ else set()
        }
        
        # 加载jieba分词
        if not chinese_model:
            jieba.initialize()
            logger.info("已加载jieba分词")
        else:
            jieba.set_dictionary(chinese_model)
            logger.info(f"已加载自定义中文词典: {chinese_model}")
        
        # 加载Transformers模型(如果需要)
        self.ner_pipeline = None
        self.keyword_pipeline = None
        
        if use_transformers:
            try:
                # NER模型
                self.ner_pipeline = pipeline(
                    "ner", 
                    model="dbmdz/bert-large-cased-finetuned-conll03-english", 
                    aggregation_strategy="simple"
                )
                logger.info("已加载命名实体识别模型")
                
                # 关键词提取模型 - 使用多语言模型
                self.keyword_pipeline = pipeline(
                    "feature-extraction", 
                    model="distilbert-base-multilingual-cased"
                )
                logger.info("已加载关键词提取模型")
                
            except Exception as e:
                logger.error(f"加载Transformers模型失败: {str(e)}")
                self.use_transformers = False
                
    def _load_chinese_stopwords(self) -> set:
        """加载中文停用词"""
        # 基本中文停用词
        basic_stopwords = set([
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', '你',
            '我', '他', '她', '它', '们', '被', '比', '把', '在', '有', '人', '上',
            '下', '之', '很', '到', '说', '去', '来', '没', '好', '也', '还', '能',
            '着', '给', '但', '如', '又', '将', '并', '等', '却', '所', '因', '已'
        ])
        
        try:
            # 尝试从nltk加载中文停用词
            from nltk.corpus import stopwords
            if 'chinese' in stopwords.fileids():
                basic_stopwords.update(set(stopwords.words('chinese')))
                
            return basic_stopwords
        except Exception as e:
            logger.warning(f"无法加载NLTK中文停用词: {str(e)}")
            return basic_stopwords
            
    def _detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 输入文本
            
        Returns:
            语言代码 ('chinese', 'english', 'unknown')
        """
        # 提取前100个字符进行语言检测
        sample = text[:100]
        
        # 计算中文字符比例
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        chinese_chars = chinese_pattern.findall(sample)
        chinese_ratio = len(chinese_chars) / len(sample) if sample else 0
        
        # 计算英文字符比例
        english_pattern = re.compile(r'[a-zA-Z]')
        english_chars = english_pattern.findall(sample)
        english_ratio = len(english_chars) / len(sample) if sample else 0
        
        # 根据比例判断语言
        if chinese_ratio > 0.3:
            return 'chinese'
        elif english_ratio > 0.3:
            return 'english'
        else:
            # 如果无法确定，默认英文
            return 'english'
            
    def extract_keywords(self, text: str, method: str = 'tfidf') -> List[Dict]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            method: 提取方法 ('tfidf', 'textrank', 'transformer', 'hybrid')
            
        Returns:
            关键词列表，每个元素为包含关键词和权重的字典
        """
        if not text or len(text.strip()) == 0:
            return []
            
        # 检测语言
        lang = self.language
        if lang == 'auto':
            lang = self._detect_language(text)
            
        logger.info(f"提取关键词，语言: {lang}, 方法: {method}")
            
        # 根据不同语言和方法提取关键词
        if method == 'tfidf':
            keywords = self._extract_by_tfidf(text, lang)
        elif method == 'textrank':
            keywords = self._extract_by_textrank(text, lang)
        elif method == 'transformer' and self.use_transformers:
            keywords = self._extract_by_transformer(text, lang)
        elif method == 'hybrid':
            # 混合方法: 结合多种算法结果
            tfidf_kw = self._extract_by_tfidf(text, lang)
            textrank_kw = self._extract_by_textrank(text, lang)
            
            # 合并两种算法的结果
            keywords = self._merge_keywords([tfidf_kw, textrank_kw])
        else:
            # 默认使用TF-IDF
            keywords = self._extract_by_tfidf(text, lang)
            
        return keywords[:self.max_keywords]
        
    def _extract_by_tfidf(self, text: str, language: str) -> List[Dict]:
        """使用TF-IDF算法提取关键词"""
        try:
            if language == 'chinese':
                # 使用jieba的TF-IDF算法
                keywords = jieba.analyse.extract_tags(
                    text, 
                    topK=self.max_keywords, 
                    withWeight=True,
                    allowPOS=('ns', 'n', 'vn', 'v', 'nz')
                )
                return [{'keyword': k, 'weight': float(w), 'type': 'tfidf'} for k, w in keywords]
                
            else:  # 英文
                # 自实现简单的TF-IDF
                words = self._tokenize_english(text)
                
                # 计算词频
                word_freq = Counter(words)
                
                # 计算TF-IDF
                max_freq = max(word_freq.values()) if word_freq else 1
                word_scores = {}
                
                for word, freq in word_freq.items():
                    # 简化的TF-IDF计算
                    tf = freq / max_freq
                    idf = math.log(1.5)  # 简化的IDF值
                    word_scores[word] = tf * idf
                    
                # 排序并返回top关键词
                sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
                return [{'keyword': k, 'weight': float(w), 'type': 'tfidf'} 
                        for k, w in sorted_words[:self.max_keywords]]
                        
        except Exception as e:
            logger.error(f"TF-IDF关键词提取失败: {str(e)}")
            return []
            
    def _extract_by_textrank(self, text: str, language: str) -> List[Dict]:
        """使用TextRank算法提取关键词"""
        try:
            if language == 'chinese':
                # 使用jieba的TextRank算法
                keywords = jieba.analyse.textrank(
                    text, 
                    topK=self.max_keywords, 
                    withWeight=True,
                    allowPOS=('ns', 'n', 'vn', 'v', 'nz')
                )
                return [{'keyword': k, 'weight': float(w), 'type': 'textrank'} for k, w in keywords]
                
            else:  # 英文
                # 目前没有内置的英文TextRank实现，返回简单的词频统计作为替代
                words = self._tokenize_english(text)
                
                # 计算词频
                word_freq = Counter(words)
                
                # 返回频率最高的词
                total_words = sum(word_freq.values())
                sorted_words = word_freq.most_common(self.max_keywords)
                
                return [{'keyword': word, 'weight': float(count/total_words), 'type': 'frequency'} 
                        for word, count in sorted_words]
                        
        except Exception as e:
            logger.error(f"TextRank关键词提取失败: {str(e)}")
            return []
            
    def _extract_by_transformer(self, text: str, language: str) -> List[Dict]:
        """使用Transformer模型提取关键词"""
        if not self.ner_pipeline or not self.keyword_pipeline:
            logger.warning("Transformer模型未加载，无法进行关键词提取")
            return []
            
        try:
            # 提取命名实体
            ner_results = self.ner_pipeline(text)
            
            # 从NER结果中获取关键实体
            entities = []
            for item in ner_results:
                if item.get('entity_group') in ['PER', 'ORG', 'LOC', 'MISC', 'PRODUCT']:
                    entities.append({
                        'keyword': item.get('word'),
                        'weight': float(item.get('score')),
                        'type': 'entity_' + item.get('entity_group')
                    })
            
            # 如果NER提取的关键词不足，使用特征提取模型补充
            if len(entities) < self.max_keywords:
                # 限制文本长度，避免过长导致处理问题
                truncated_text = text[:500]
                
                # 获取文本特征向量
                features = self.keyword_pipeline(truncated_text)
                
                # 简单处理: 分词并计算每个词的特征向量范数作为重要性指标
                if language == 'chinese':
                    words = list(jieba.cut(truncated_text))
                else:
                    words = self._tokenize_english(truncated_text)
                    
                # 去除停用词
                stop_words = self.stop_words[language]
                words = [w for w in words if w not in stop_words and len(w) > 1]
                
                # 根据特征向量计算重要性
                word_scores = Counter()
                for word in words:
                    word_scores[word] += 1  # 简化处理，仅使用词频
                
                # 添加剩余需要的关键词
                remaining_keywords = self.max_keywords - len(entities)
                for word, score in word_scores.most_common(remaining_keywords):
                    entities.append({
                        'keyword': word,
                        'weight': float(score / len(words)) if len(words) > 0 else 0,
                        'type': 'transformer'
                    })
                
            return entities[:self.max_keywords]
            
        except Exception as e:
            logger.error(f"Transformer关键词提取失败: {str(e)}")
            return []
            
    def _tokenize_english(self, text: str) -> List[str]:
        """对英文文本进行分词和预处理"""
        # 转小写
        text = text.lower()
        
        # 去除标点符号
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # 分词
        words = text.split()
        
        # 去除停用词
        english_stopwords = self.stop_words['english']
        words = [word for word in words if word not in english_stopwords and len(word) > 1]
        
        return words
        
    def _merge_keywords(self, keyword_lists: List[List[Dict]]) -> List[Dict]:
        """合并多个关键词列表，进行加权融合"""
        # 合并所有关键词
        keyword_scores = {}
        
        for keyword_list in keyword_lists:
            for item in keyword_list:
                keyword = item['keyword']
                weight = item['weight']
                
                if keyword not in keyword_scores:
                    keyword_scores[keyword] = {
                        'total_weight': 0,
                        'count': 0,
                        'types': set()
                    }
                    
                keyword_scores[keyword]['total_weight'] += weight
                keyword_scores[keyword]['count'] += 1
                keyword_scores[keyword]['types'].add(item.get('type', 'unknown'))
        
        # 计算平均权重并排序
        merged_keywords = []
        for keyword, info in keyword_scores.items():
            avg_weight = info['total_weight'] / info['count']
            
            # 关键词出现在多种算法中权重更高
            algorithm_bonus = min(info['count'] * 0.1, 0.3)
            
            merged_keywords.append({
                'keyword': keyword,
                'weight': float(avg_weight + algorithm_bonus),
                'type': '+'.join(info['types'])
            })
            
        # 按权重排序
        merged_keywords.sort(key=lambda x: x['weight'], reverse=True)
        
        return merged_keywords[:self.max_keywords]
    
    def extract_topics(self, text: str, num_topics: int = 3) -> List[Dict]:
        """
        从文本中提取主题
        
        Args:
            text: 输入文本
            num_topics: 主题数量
            
        Returns:
            主题列表，包含主题名称和关键词
        """
        # 检测语言
        lang = self.language
        if lang == 'auto':
            lang = self._detect_language(text)
            
        # 提取关键词(使用混合方法)
        keywords = self.extract_keywords(text, method='hybrid')
        
        # 简单实现：将关键词按权重分组作为主题
        topics = []
        
        # 确保主题数量不超过关键词数量
        actual_topics = min(num_topics, len(keywords) // 2)
        
        if actual_topics > 0:
            # 每个主题包含的关键词数量
            keywords_per_topic = len(keywords) // actual_topics
            
            for i in range(actual_topics):
                start_idx = i * keywords_per_topic
                end_idx = start_idx + keywords_per_topic
                
                topic_keywords = keywords[start_idx:end_idx]
                
                # 使用最高权重的关键词作为主题名称
                topic_name = topic_keywords[0]['keyword'] if topic_keywords else f"主题_{i+1}"
                
                topics.append({
                    'name': topic_name,
                    'keywords': topic_keywords,
                    'weight': float(sum(k['weight'] for k in topic_keywords) / len(topic_keywords))
                })
                
        return sorted(topics, key=lambda x: x['weight'], reverse=True)


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建关键词提取器
    generator = KeywordGenerator(language='auto', max_keywords=10)
    
    # 测试中文文本
    chinese_text = """
    随着人工智能技术的发展，深度学习在计算机视觉、自然语言处理和语音识别等领域取得了显著进展。
    近年来，大型语言模型如GPT和BERT通过自监督学习方法，能够生成高质量的文本内容，理解上下文语境，
    回答问题并执行各种语言任务。这些模型的出现极大地推动了智能助手、自动写作和实时翻译等应用的发展。
    然而，人工智能技术的广泛应用也带来了伦理和隐私等方面的挑战，需要社会各界共同关注和解决。
    """
    
    print("===== 中文文本关键词提取 =====")
    chinese_keywords = generator.extract_keywords(chinese_text, method='hybrid')
    print("关键词:")
    for kw in chinese_keywords:
        print(f"  - {kw['keyword']}: {kw['weight']:.4f} ({kw['type']})")
        
    chinese_topics = generator.extract_topics(chinese_text)
    print("\n主题:")
    for topic in chinese_topics:
        print(f"  - {topic['name']}: {topic['weight']:.4f}")
        print(f"    关键词: {', '.join(k['keyword'] for k in topic['keywords'][:3])}")
    
    # 测试英文文本
    english_text = """
    Artificial intelligence (AI) is revolutionizing industries across the globe. 
    Machine learning algorithms, particularly deep neural networks, have shown remarkable 
    performance in tasks like image recognition, natural language understanding, and game playing.
    Companies like Google, Microsoft, and OpenAI are investing heavily in developing more 
    advanced AI systems. However, concerns about privacy, bias, and ethical implications 
    continue to grow as these technologies become more integrated into our daily lives.
    """
    
    print("\n===== 英文文本关键词提取 =====")
    english_keywords = generator.extract_keywords(english_text, method='hybrid')
    print("关键词:")
    for kw in english_keywords:
        print(f"  - {kw['keyword']}: {kw['weight']:.4f} ({kw['type']})")
        
    english_topics = generator.extract_topics(english_text)
    print("\n主题:")
    for topic in english_topics:
        print(f"  - {topic['name']}: {topic['weight']:.4f}")
        print(f"    关键词: {', '.join(k['keyword'] for k in topic['keywords'][:3])}") 
 