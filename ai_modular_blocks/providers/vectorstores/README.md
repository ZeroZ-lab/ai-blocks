# Vector Store Providers

向量存储提供商实现

## 🎯 目录说明

本目录包含各种向量数据库和存储服务的具体实现，统一实现`VectorStore`接口。

## 📁 提供商列表

### `pinecone.py` - Pinecone云向量数据库
- **类型**: 云服务
- **特点**: 高性能、托管服务、自动扩展
- **适用**: 生产环境、大规模应用
- **功能**: 元数据过滤、近似搜索、实时更新

### `chroma.py` - Chroma本地向量数据库
- **类型**: 嵌入式数据库
- **特点**: 轻量级、易部署、开源
- **适用**: 开发测试、小到中型应用
- **功能**: 本地存储、内存索引、简单部署

### `faiss.py` - Facebook FAISS
- **类型**: 向量索引库
- **特点**: 高性能、CPU/GPU支持、多种算法
- **适用**: 研究、高性能计算
- **功能**: 多种索引类型、批量搜索、内存优化

### `qdrant.py` - Qdrant向量数据库
- **类型**: 专用向量数据库
- **特点**: Rust实现、高并发、丰富过滤
- **适用**: 高并发场景、复杂查询
- **功能**: 有效载荷过滤、集群支持、REST API

### `memory.py` - 内存向量存储
- **类型**: 内存存储
- **特点**: 快速访问、简单实现、易测试
- **适用**: 测试、小数据集、原型开发
- **功能**: 纯内存操作、简单相似性计算

## 📖 使用示例

```python
from ai_modular_blocks.providers.vectorstores import PineconeProvider
from ai_modular_blocks.core.types import VectorStoreConfig, VectorDocument

# 配置Pinecone
config = VectorStoreConfig(
    api_key="your-pinecone-key",
    index_name="my-index", 
    dimension=1536,
    metric="cosine"
)

# 初始化向量存储
vector_store = PineconeProvider(config)
await vector_store.initialize()

# 存储文档
documents = [
    VectorDocument(
        id="doc1",
        content="AI is transforming the world",
        metadata={"category": "tech", "date": "2024-01-01"},
        embedding=[0.1, 0.2, 0.3, ...]  # 1536维向量
    )
]

result = await vector_store.upsert(documents)
print(f"存储了 {result['processed_count']} 个文档")

# 搜索相似文档
query_vector = [0.1, 0.15, 0.25, ...]  # 查询向量
results = await vector_store.search(
    query_vector=query_vector,
    top_k=5,
    filter_dict={"category": "tech"},  # 元数据过滤
    include_metadata=True
)

for result in results:
    print(f"文档: {result.document.content}")
    print(f"相似度: {result.score}")
    print(f"元数据: {result.document.metadata}")
```

## 🔧 实现指南

### 基础实现结构
```python
from ai_modular_blocks.core.base import BaseVectorStore
from ai_modular_blocks.core.types import VectorStoreConfig

class MyVectorStore(BaseVectorStore):
    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)
        self.client = None
    
    async def _initialize_provider(self):
        """初始化向量数据库连接"""
        self.client = create_client(self.config)
    
    async def _upsert_batch_impl(self, documents, namespace):
        """批量插入/更新文档"""
        # 转换文档格式
        vectors = self._convert_documents_to_vectors(documents)
        # 调用向量数据库API
        return await self.client.upsert(vectors, namespace=namespace)
    
    async def _search_impl(self, query_vector, top_k, filter_dict, namespace, include_metadata, include_values):
        """搜索相似向量"""
        results = await self.client.search(
            vector=query_vector,
            top_k=top_k,
            filter=filter_dict,
            namespace=namespace
        )
        return self._convert_results_to_search_results(results)
```

### 配置管理
```python
# 每个提供商都有特定的配置需求
class PineconeConfig(VectorStoreConfig):
    def __init__(self, api_key: str, index_name: str, environment: str = "us-west1-gcp", **kwargs):
        super().__init__(api_key=api_key, index_name=index_name, **kwargs)
        self.environment = environment

class ChromaConfig(VectorStoreConfig):
    def __init__(self, persist_directory: str = "./chroma_db", **kwargs):
        super().__init__(api_key="", index_name="default", **kwargs)
        self.persist_directory = persist_directory
```

### 错误处理
```python
from ai_modular_blocks.core.exceptions import ProviderException

async def _search_impl(self, query_vector, top_k, **kwargs):
    try:
        results = await self.client.search(...)
        return results
    except VectorDBTimeoutError as e:
        raise TimeoutException(f"Vector search timeout: {e}", timeout_duration=30.0)
    except VectorDBAuthError as e:
        raise AuthenticationException(f"Vector DB auth failed: {e}")
    except Exception as e:
        raise ProviderException(f"Vector search failed: {e}", provider_name=self.provider_name)
```

## 🚀 性能优化

### 批量操作
```python
async def upsert_large_dataset(self, documents: DocumentList, batch_size: int = 100):
    """优化大数据集的批量插入"""
    total_processed = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # 并行处理批次
        result = await self._upsert_batch_impl(batch, namespace=None)
        total_processed += result.get("processed_count", 0)
        
        # 避免API限流
        if i % 1000 == 0:
            await asyncio.sleep(0.1)
    
    return {"total_processed": total_processed}
```

### 搜索优化
```python
async def search_with_cache(self, query_vector, top_k=5, **kwargs):
    """带缓存的向量搜索"""
    # 生成缓存键
    cache_key = self._generate_search_cache_key(query_vector, top_k, kwargs)
    
    # 尝试从缓存获取
    if self.cache:
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
    
    # 执行搜索
    results = await self._search_impl(query_vector, top_k, **kwargs)
    
    # 缓存结果
    if self.cache:
        await self.cache.set(cache_key, results, ttl=300)  # 5分钟缓存
    
    return results
```

## 🔍 选择指南

### Pinecone - 生产环境推荐
- ✅ 高可用性和自动扩展
- ✅ 企业级安全和支持  
- ✅ 优秀的查询性能
- ❌ 需要网络连接
- ❌ 按使用量付费

### Chroma - 本地开发推荐
- ✅ 简单易用，快速搭建
- ✅ 完全本地化，无网络依赖
- ✅ 开源免费
- ❌ 扩展能力有限
- ❌ 需要自维护

### FAISS - 高性能计算推荐  
- ✅ 极高的搜索性能
- ✅ 多种索引算法
- ✅ CPU/GPU加速支持
- ❌ 学习曲线较陡
- ❌ 需要更多内存

### Qdrant - 高并发场景推荐
- ✅ 高并发处理能力
- ✅ 丰富的过滤功能
- ✅ 集群支持
- ❌ 相对较新的技术
- ❌ 社区生态较小

## 🧪 测试和验证

```python
# 向量存储测试示例
@pytest.mark.asyncio
async def test_vector_store_basic_operations(vector_store):
    """测试向量存储基本操作"""
    
    # 测试数据
    test_docs = [
        VectorDocument(
            id="test1",
            content="测试文档1", 
            metadata={"type": "test"},
            embedding=[random.random() for _ in range(1536)]
        )
    ]
    
    # 测试插入
    upsert_result = await vector_store.upsert(test_docs)
    assert upsert_result["processed_count"] == 1
    
    # 测试搜索
    query_vector = [random.random() for _ in range(1536)]
    search_results = await vector_store.search(query_vector, top_k=1)
    assert len(search_results) > 0
    
    # 测试删除
    delete_result = await vector_store.delete(["test1"])
    assert delete_result["deleted_count"] == 1
```

## 🎯 最佳实践

1. **索引设计** - 根据查询模式选择合适的索引类型
2. **批量操作** - 使用批量插入和更新提高性能
3. **元数据优化** - 合理设计元数据结构支持高效过滤
4. **监控指标** - 跟踪查询延迟、吞吐量和存储使用量
5. **备份策略** - 重要数据的定期备份和恢复机制
