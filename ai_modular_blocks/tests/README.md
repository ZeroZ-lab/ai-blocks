# Tests Module

测试模块 - AI Modular Blocks的质量保证层

## 🎯 测试策略

遵循"**测试金字塔**"原则，确保代码质量和系统可靠性：

```
    🔺 E2E Tests (少量)
   🔺🔺 Integration Tests (适量)  
  🔺🔺🔺 Unit Tests (大量)
```

## 📁 目录组织

### `unit/` - 单元测试
测试单个模块、类和函数的功能：

```
unit/
├── core/
│   ├── test_types.py         # 类型定义测试
│   ├── test_interfaces.py    # 接口定义测试
│   ├── test_base.py          # 基础类测试
│   ├── test_config.py        # 配置管理测试
│   ├── test_exceptions.py    # 异常处理测试
│   └── test_validators.py    # 验证器测试
├── providers/
│   ├── test_llm_providers.py # LLM提供商测试
│   ├── test_vector_stores.py # 向量存储测试
│   ├── test_embeddings.py    # 嵌入服务测试
│   └── test_tools.py         # 工具提供商测试
├── processors/
│   ├── test_loaders.py       # 文档加载器测试
│   ├── test_splitters.py     # 文档分割器测试
│   └── test_transformers.py  # 文档转换器测试
└── utils/
    ├── test_caching.py       # 缓存系统测试
    ├── test_logging.py       # 日志系统测试
    └── test_monitoring.py    # 监控系统测试
```

**特点**: 快速执行、无外部依赖、高覆盖率

### `integration/` - 集成测试
测试组件间的交互和与外部服务的集成：

```
integration/
├── test_llm_integration.py    # LLM服务集成测试
├── test_vector_integration.py # 向量数据库集成测试
├── test_cache_integration.py  # 缓存服务集成测试
├── test_rag_pipeline.py       # RAG流水线集成测试
├── test_tool_execution.py     # 工具执行集成测试
└── test_mcp_protocol.py       # MCP协议集成测试
```

**特点**: 真实环境、外部依赖、端到端场景

### `performance/` - 性能测试
测试系统的性能、并发和负载能力：

```
performance/
├── test_llm_throughput.py     # LLM吞吐量测试
├── test_vector_search.py      # 向量搜索性能测试
├── test_concurrent_requests.py # 并发请求测试
├── test_memory_usage.py       # 内存使用测试
├── test_cache_performance.py  # 缓存性能测试
└── benchmarks/
    ├── llm_benchmark.py       # LLM性能基准
    ├── vector_benchmark.py    # 向量操作基准
    └── end_to_end_benchmark.py # 端到端性能基准
```

**特点**: 性能指标、资源监控、基准对比

## 🧪 测试工具和框架

### 核心测试框架
```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from ai_modular_blocks.tests.fixtures import *
```

### 常用测试装饰器
```python
@pytest.mark.asyncio      # 异步测试
@pytest.mark.unit         # 单元测试标记
@pytest.mark.integration  # 集成测试标记
@pytest.mark.performance  # 性能测试标记
@pytest.mark.slow         # 慢速测试标记
@pytest.mark.external     # 需要外部服务的测试
```

### Mock和Fixture
```python
# tests/fixtures/llm_fixtures.py
import pytest
from unittest.mock import AsyncMock
from ai_modular_blocks.core.types import LLMResponse

@pytest.fixture
def mock_llm_provider():
    """Mock LLM Provider fixture"""
    provider = AsyncMock()
    provider.chat_completion.return_value = LLMResponse(
        content="Test response",
        model="test-model",
        usage={"prompt_tokens": 10, "completion_tokens": 5},
        created_at=datetime.now(),
        finish_reason="stop"
    )
    return provider

@pytest.fixture
async def real_openai_provider():
    """真实的OpenAI Provider（需要API密钥）"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("需要OPENAI_API_KEY环境变量")
    
    config = LLMConfig(api_key=os.getenv("OPENAI_API_KEY"))
    provider = OpenAIProvider(config)
    await provider.initialize()
    yield provider
    await provider.cleanup()
```

## 📖 测试示例

### 单元测试示例
```python
# tests/unit/core/test_validators.py
import pytest
from ai_modular_blocks.core.validators import InputValidator
from ai_modular_blocks.core.exceptions import ValidationException
from ai_modular_blocks.core.types import ChatMessage

class TestInputValidator:
    
    def test_validate_api_key_valid(self):
        """测试有效API密钥验证"""
        api_key = "sk-test1234567890abcdef1234567890abcdef123456"
        result = InputValidator.validate_api_key(api_key, "openai")
        assert result == api_key
    
    def test_validate_api_key_invalid_format(self):
        """测试无效API密钥格式"""
        with pytest.raises(ValidationException) as exc_info:
            InputValidator.validate_api_key("invalid-key", "openai")
        
        assert "Invalid API key format" in str(exc_info.value)
    
    def test_validate_chat_message_valid(self):
        """测试有效聊天消息验证"""
        message = ChatMessage(role="user", content="Hello")
        result = InputValidator.validate_chat_message(message)
        assert result == message
    
    @pytest.mark.parametrize("role", ["invalid", "bot", ""])
    def test_validate_chat_message_invalid_role(self, role):
        """测试无效角色验证"""
        message = ChatMessage(role=role, content="Hello")
        with pytest.raises(ValidationException):
            InputValidator.validate_chat_message(message)
```

### 集成测试示例
```python
# tests/integration/test_rag_pipeline.py
import pytest
from ai_modular_blocks.core.types import ChatMessage, VectorDocument
from ai_modular_blocks.providers.llm import OpenAIProvider
from ai_modular_blocks.providers.vectorstores import ChromaProvider
from ai_modular_blocks.providers.embeddings import OpenAIEmbeddingProvider

@pytest.mark.integration
@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end(
    openai_config,
    chroma_config,
    sample_documents
):
    """测试完整的RAG流水线"""
    
    # 初始化组件
    llm = OpenAIProvider(openai_config)
    vector_store = ChromaProvider(chroma_config)
    embedding = OpenAIEmbeddingProvider(openai_config)
    
    await llm.initialize()
    await vector_store.initialize()
    await embedding.initialize()
    
    try:
        # 1. 嵌入和存储文档
        embedded_docs = await embedding.embed_documents(sample_documents)
        upsert_result = await vector_store.upsert(embedded_docs)
        assert upsert_result["processed_count"] == len(sample_documents)
        
        # 2. 搜索相关文档
        query = "What is the capital of France?"
        query_embedding = await embedding.embed_text([query])
        search_results = await vector_store.search(
            query_embedding[0], 
            top_k=3
        )
        assert len(search_results) > 0
        
        # 3. 生成回答
        context = "\n".join([result.document.content for result in search_results])
        messages = [
            ChatMessage(role="system", content=f"Context: {context}"),
            ChatMessage(role="user", content=query)
        ]
        
        response = await llm.chat_completion(messages, model="gpt-3.5-turbo")
        assert response.content
        assert len(response.content) > 0
        
    finally:
        await llm.cleanup()
        await vector_store.cleanup()
        await embedding.cleanup()
```

### 性能测试示例
```python
# tests/performance/test_llm_throughput.py
import asyncio
import time
import pytest
from ai_modular_blocks.providers.llm import OpenAIProvider

@pytest.mark.performance
@pytest.mark.asyncio
async def test_llm_concurrent_requests(openai_provider):
    """测试LLM并发请求性能"""
    
    messages = [ChatMessage(role="user", content="Say hello")]
    
    async def single_request():
        start_time = time.time()
        response = await openai_provider.chat_completion(
            messages, 
            model="gpt-3.5-turbo"
        )
        end_time = time.time()
        return {
            "duration": end_time - start_time,
            "response_length": len(response.content),
            "tokens_used": response.usage.get("total_tokens", 0)
        }
    
    # 并发执行多个请求
    concurrent_requests = 10
    start_time = time.time()
    
    tasks = [single_request() for _ in range(concurrent_requests)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # 性能断言
    assert total_time < 30  # 10个请求在30秒内完成
    
    avg_duration = sum(r["duration"] for r in results) / len(results)
    assert avg_duration < 5  # 平均响应时间小于5秒
    
    # 记录性能指标
    print(f"并发请求数: {concurrent_requests}")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均响应时间: {avg_duration:.2f}秒")
    print(f"QPS: {concurrent_requests / total_time:.2f}")
```

## 🚀 运行测试

### 基本测试命令
```bash
# 运行所有测试
pytest

# 运行特定类型的测试
pytest -m unit           # 只运行单元测试
pytest -m integration    # 只运行集成测试
pytest -m performance    # 只运行性能测试

# 运行特定文件或目录
pytest tests/unit/core/
pytest tests/integration/test_rag_pipeline.py

# 生成覆盖率报告
pytest --cov=ai_modular_blocks --cov-report=html

# 详细输出
pytest -v -s

# 并行执行（需要pytest-xdist）
pytest -n auto
```

### 环境配置
```bash
# 设置测试环境变量
export OPENAI_API_KEY="your-api-key"
export PINECONE_API_KEY="your-pinecone-key"
export TEST_ENV="testing"

# 或使用 .env.test 文件
cp .env.example .env.test
# 编辑 .env.test 文件
```

### Docker测试环境
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-runner:
    build: .
    environment:
      - TEST_ENV=docker
    volumes:
      - .:/app
    command: pytest tests/
  
  redis-test:
    image: redis:alpine
    ports:
      - "6380:6379"
  
  chroma-test:
    image: chromadb/chroma
    ports:
      - "8001:8000"
```

## 🔧 测试配置

### pytest.ini配置
```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra 
    --strict-markers 
    --strict-config 
    --cov=ai_modular_blocks
    --cov-branch
    --cov-report=term-missing
    --cov-fail-under=80

testpaths = tests

markers =
    unit: Unit tests
    integration: Integration tests  
    performance: Performance tests
    slow: Slow running tests
    external: Tests requiring external services

asyncio_mode = auto
```

### conftest.py配置
```python
# tests/conftest.py
import pytest
import asyncio
import os
from unittest.mock import AsyncMock

# 全局测试配置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环供整个测试会话使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """为每个测试设置环境"""
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

# Mock fixtures
@pytest.fixture
def mock_openai_client():
    return AsyncMock()

# 配置fixtures
@pytest.fixture
def test_config():
    return {
        "llm": {
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-3.5-turbo"
        },
        "vector_store": {
            "provider": "chroma",
            "collection_name": "test-collection"
        }
    }
```

## 🎯 测试最佳实践

### 1. 测试命名约定
```python
def test_[unit_under_test]_[scenario]_[expected_result]():
    """测试函数命名应该清晰描述测试内容"""
    pass

# 好的例子
def test_llm_provider_chat_completion_with_valid_input_returns_response():
def test_vector_store_search_with_empty_query_raises_validation_error():
def test_cache_get_with_expired_key_returns_none():
```

### 2. AAA模式（Arrange-Act-Assert）
```python
async def test_llm_chat_completion_success():
    # Arrange - 准备测试数据
    provider = OpenAIProvider(test_config)
    messages = [ChatMessage(role="user", content="Hello")]
    
    # Act - 执行测试操作
    response = await provider.chat_completion(messages, "gpt-3.5-turbo")
    
    # Assert - 验证结果
    assert response.content is not None
    assert response.model == "gpt-3.5-turbo"
    assert response.usage["total_tokens"] > 0
```

### 3. 测试隔离和清理
```python
@pytest.fixture
async def clean_vector_store():
    """确保每个测试都有干净的向量存储"""
    store = ChromaProvider(test_config)
    await store.initialize()
    
    yield store
    
    # 清理测试数据
    await store.clear_collection()
    await store.cleanup()
```

### 4. 参数化测试
```python
@pytest.mark.parametrize("model,expected_provider", [
    ("gpt-3.5-turbo", "openai"),
    ("claude-3", "anthropic"),
    ("llama-2", "huggingface"),
])
def test_model_provider_mapping(model, expected_provider):
    provider = get_provider_for_model(model)
    assert provider.provider_type == expected_provider
```

## 🛡️ 测试质量保证

### 代码覆盖率要求
- **单元测试**: ≥ 90%覆盖率
- **集成测试**: ≥ 70%覆盖率  
- **关键路径**: 100%覆盖率

### 性能基准
- **LLM请求**: < 5秒响应时间
- **向量搜索**: < 100ms查询时间
- **缓存操作**: < 10ms访问时间

### 测试数据管理
```python
# tests/data/sample_data.py
SAMPLE_DOCUMENTS = [
    VectorDocument(
        id="doc1",
        content="Paris is the capital of France.",
        metadata={"source": "geography", "topic": "capitals"}
    ),
    # 更多样本数据...
]

SAMPLE_MESSAGES = [
    ChatMessage(role="user", content="Hello"),
    ChatMessage(role="assistant", content="Hi there!"),
    # 更多样本消息...
]
```

## 🔍 调试和故障排除

### 测试调试
```python
# 使用pytest调试
pytest --pdb                    # 测试失败时进入调试器
pytest --pdb-trace             # 测试开始时进入调试器
pytest -s                      # 显示print输出
pytest --lf                    # 只运行上次失败的测试
pytest --tb=short              # 简短的错误回溯
```

### 日志配置
```python
# tests/conftest.py
import logging

@pytest.fixture(autouse=True)
def configure_test_logging():
    """为测试配置日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### CI/CD集成
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run unit tests
      run: pytest tests/unit/ -v
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```
