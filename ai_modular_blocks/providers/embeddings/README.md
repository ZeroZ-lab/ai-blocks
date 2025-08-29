# Embedding Providers

嵌入服务提供商实现

## 🎯 目录说明

本目录包含各种文本嵌入服务和模型的具体实现，统一实现`EmbeddingProvider`接口。

## 📁 提供商列表

### `openai.py` - OpenAI Embedding API
- **模型**: text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
- **维度**: 1536 (ada-002), 可配置 (3-small/large)
- **特点**: 高质量、多语言支持、API稳定
- **适用**: 生产环境、多语言应用

### `huggingface.py` - HuggingFace Embedding模型
- **模型**: sentence-transformers, BERT系列, 自定义模型
- **维度**: 模型相关 (384-1024常见)
- **特点**: 开源、可本地部署、模型丰富
- **适用**: 离线环境、自定义需求

### `sentence_transformers.py` - SentenceTransformers
- **模型**: all-MiniLM-L6-v2, all-mpnet-base-v2等
- **维度**: 384-768
- **特点**: 轻量级、快速推理、易部署
- **适用**: 快速原型、资源受限环境

### `cohere.py` - Cohere Embedding API
- **模型**: embed-english-v3.0, embed-multilingual-v3.0
- **维度**: 1024-4096可配置
- **特点**: 语义质量高、支持压缩、多语言
- **适用**: 高质量需求、多语言场景

### `local.py` - 本地嵌入模型
- **模型**: ONNX, TensorRT, 自定义格式
- **维度**: 模型相关
- **特点**: 完全离线、自主可控、高性能
- **适用**: 私有部署、高安全要求

## 📖 使用示例

```python
from ai_modular_blocks.providers.embeddings import OpenAIEmbeddingProvider
from ai_modular_blocks.core.types import EmbeddingConfig

# 配置OpenAI嵌入服务
config = EmbeddingConfig(
    api_key="sk-...",
    model="text-embedding-3-small",
    dimension=1536
)

# 初始化嵌入提供商
embedding = OpenAIEmbeddingProvider(config)
await embedding.initialize()

# 嵌入单个文本
texts = ["Hello world", "AI is amazing", "Vector databases are useful"]
embeddings = await embedding.embed_text(texts)

print(f"生成了 {len(embeddings)} 个嵌入向量")
print(f"向量维度: {len(embeddings[0])}")

# 嵌入文档
from ai_modular_blocks.core.types import VectorDocument

documents = [
    VectorDocument(
        id="doc1",
        content="人工智能正在改变世界",
        metadata={"language": "zh", "topic": "AI"}
    ),
    VectorDocument(
        id="doc2", 
        content="Machine learning enables intelligent systems",
        metadata={"language": "en", "topic": "ML"}
    )
]

embedded_docs = await embedding.embed_documents(documents)

for doc in embedded_docs:
    print(f"文档 {doc.id}: 嵌入维度 {len(doc.embedding)}")
```

## 🔧 实现指南

### 基础实现结构
```python
from ai_modular_blocks.core.base import BaseEmbeddingProvider
from ai_modular_blocks.core.types import EmbeddingConfig

class MyEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.client = None
        self.model = config.model
    
    async def _initialize_provider(self):
        """初始化嵌入服务连接"""
        self.client = create_embedding_client(self.config)
    
    async def _embed_text_impl(self, texts: List[str], model: Optional[str], **kwargs):
        """实现文本嵌入逻辑"""
        model = model or self.model
        
        try:
            # 调用嵌入API或模型
            response = await self.client.embed(texts, model=model)
            
            # 提取嵌入向量
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
            
        except Exception as e:
            raise ProviderException(f"Embedding failed: {e}", provider_name=self.provider_name)
    
    def get_embedding_dimension(self, model: Optional[str] = None) -> int:
        """返回嵌入向量维度"""
        model = model or self.model
        return self._get_model_dimension(model)
```

### 批量处理优化
```python
async def embed_text_batched(self, texts: List[str], batch_size: int = 100, **kwargs):
    """批量处理大量文本"""
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # 处理批次
        batch_embeddings = await self._embed_text_impl(batch, **kwargs)
        all_embeddings.extend(batch_embeddings)
        
        # 添加延迟避免API限流
        if i % 1000 == 0:
            await asyncio.sleep(0.1)
    
    return all_embeddings
```

### 缓存支持
```python
async def embed_text_with_cache(self, texts: List[str], **kwargs):
    """带缓存的文本嵌入"""
    cached_embeddings = []
    uncached_texts = []
    uncached_indices = []
    
    # 检查缓存
    for i, text in enumerate(texts):
        cache_key = self._generate_cache_key(text, kwargs)
        cached_embedding = await self.cache.get(cache_key) if self.cache else None
        
        if cached_embedding:
            cached_embeddings.append((i, cached_embedding))
        else:
            uncached_texts.append(text)
            uncached_indices.append(i)
    
    # 处理未缓存的文本
    if uncached_texts:
        new_embeddings = await self._embed_text_impl(uncached_texts, **kwargs)
        
        # 缓存新嵌入
        if self.cache:
            for text, embedding in zip(uncached_texts, new_embeddings):
                cache_key = self._generate_cache_key(text, kwargs)
                await self.cache.set(cache_key, embedding, ttl=3600)
    
    # 合并结果
    final_embeddings = [None] * len(texts)
    
    for i, embedding in cached_embeddings:
        final_embeddings[i] = embedding
    
    for i, embedding in zip(uncached_indices, new_embeddings):
        final_embeddings[i] = embedding
    
    return final_embeddings
```

## 🚀 性能优化策略

### 1. 并发处理
```python
import asyncio

async def embed_documents_concurrent(self, documents: DocumentList, max_concurrent: int = 10):
    """并发处理文档嵌入"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def embed_single_doc(doc):
        async with semaphore:
            texts = [doc.content]
            embeddings = await self._embed_text_impl(texts)
            doc.embedding = embeddings[0]
            return doc
    
    tasks = [embed_single_doc(doc) for doc in documents]
    embedded_docs = await asyncio.gather(*tasks)
    
    return embedded_docs
```

### 2. 智能分块
```python
def chunk_text_for_embedding(self, text: str, max_tokens: int = 8000) -> List[str]:
    """智能分块长文本"""
    # 简单实现，实际可能需要更复杂的逻辑
    sentences = text.split('.')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_tokens:
            current_chunk += sentence + "."
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

### 3. 模型预热
```python
async def warmup_model(self):
    """预热嵌入模型"""
    warmup_texts = ["Hello", "Test", "Warmup"]
    await self._embed_text_impl(warmup_texts)
    self.logger.info("Embedding model warmed up")
```

## 🔍 模型选择指南

### OpenAI - 高质量通用推荐
- ✅ 优秀的语义理解
- ✅ 多语言支持良好
- ✅ API稳定可靠
- ❌ 需要网络连接
- ❌ 按使用量付费

### SentenceTransformers - 轻量级推荐
- ✅ 快速推理
- ✅ 模型选择丰富
- ✅ 完全免费
- ❌ 质量可能不如商业API
- ❌ 需要本地部署

### Cohere - 多语言场景推荐
- ✅ 多语言质量优秀
- ✅ 支持嵌入压缩
- ✅ 针对搜索优化
- ❌ 相对较新
- ❌ 生态系统较小

### HuggingFace - 自定义需求推荐
- ✅ 模型种类最丰富
- ✅ 支持微调
- ✅ 开源社区活跃
- ❌ 需要更多技术知识
- ❌ 部署复杂度较高

## 🧪 质量评估

### 语义相似性测试
```python
async def test_semantic_similarity(self):
    """测试语义相似性质量"""
    test_pairs = [
        ("狗是动物", "犬类属于动物界"),      # 应该高相似
        ("今天天气很好", "股票市场波动"),    # 应该低相似
        ("机器学习", "人工智能"),           # 应该中等相似
    ]
    
    for text1, text2 in test_pairs:
        emb1 = await self.embed_text([text1])
        emb2 = await self.embed_text([text2])
        
        similarity = cosine_similarity(emb1[0], emb2[0])
        print(f"'{text1}' vs '{text2}': {similarity:.3f}")

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    import numpy as np
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

### 嵌入质量基准测试
```python
async def benchmark_embedding_quality(self, test_dataset):
    """基准测试嵌入质量"""
    results = {
        "avg_processing_time": 0,
        "embedding_dimension": 0,
        "similarity_scores": []
    }
    
    start_time = time.time()
    
    for sample in test_dataset:
        # 嵌入查询和文档
        query_emb = await self.embed_text([sample.query])
        doc_embs = await self.embed_text(sample.documents)
        
        # 计算相似度
        similarities = [
            cosine_similarity(query_emb[0], doc_emb) 
            for doc_emb in doc_embs
        ]
        
        results["similarity_scores"].extend(similarities)
    
    results["avg_processing_time"] = (time.time() - start_time) / len(test_dataset)
    results["embedding_dimension"] = len(query_emb[0])
    
    return results
```

## 🎯 最佳实践

1. **模型选择** - 根据应用场景选择合适的模型
2. **批量处理** - 使用批量API提高效率
3. **缓存策略** - 缓存常用文本的嵌入结果
4. **错误处理** - 优雅处理API限流和网络错误
5. **监控指标** - 跟踪嵌入质量和性能指标
6. **成本控制** - 合理使用API以控制成本
7. **安全考虑** - 保护API密钥和敏感数据

## 🔧 故障排除

### 常见问题
- **API限流**: 实现退避重试策略
- **维度不匹配**: 确保向量存储配置正确
- **内存溢出**: 使用批量处理和流式处理
- **质量问题**: 选择更适合的模型或调整预处理
