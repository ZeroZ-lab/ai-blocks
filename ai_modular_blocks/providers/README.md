# Providers Module

提供商实现模块 - AI Modular Blocks的具体实现层

## 🎯 职责范围

实现core/interfaces/中定义的所有抽象接口，提供与各种第三方服务和本地工具的具体集成。

## 📁 目录组织

### `llm/` - 大语言模型提供商
集成各大LLM服务商的具体实现：

```
llm/
├── openai.py      # OpenAI GPT系列模型
├── anthropic.py   # Anthropic Claude系列模型  
├── huggingface.py # HuggingFace模型
├── local.py       # 本地部署模型
└── mock.py        # 测试用Mock实现
```

**支持功能**: 聊天补全、流式响应、Function Calling、模型切换

### `vectorstores/` - 向量存储提供商
集成各种向量数据库的具体实现：

```
vectorstores/
├── pinecone.py    # Pinecone云向量数据库
├── chroma.py      # Chroma本地向量数据库
├── faiss.py       # Facebook FAISS
├── qdrant.py      # Qdrant向量数据库
└── memory.py      # 内存向量存储（测试用）
```

**支持功能**: 向量存储、相似性搜索、元数据过滤、批量操作

### `embeddings/` - 嵌入服务提供商
集成各种文本嵌入服务的具体实现：

```
embeddings/
├── openai.py      # OpenAI Embedding API
├── huggingface.py # HuggingFace嵌入模型
├── sentence_transformers.py # SentenceTransformers
├── cohere.py      # Cohere嵌入服务
└── local.py       # 本地嵌入模型
```

**支持功能**: 文本向量化、批量嵌入、维度配置、模型选择

### `tools/` - 工具提供商
集成各种工具和Function Calling的具体实现：

```
tools/
├── builtin/       # 内置工具（计算器、时间等）
├── web/           # Web工具（搜索、爬虫等）
├── filesystem/    # 文件系统工具
├── database/      # 数据库工具
└── custom/        # 自定义工具框架
```

**支持功能**: 工具注册、并行执行、参数验证、结果处理

## 🔧 实现规范

### 1. 继承基础类
所有Provider都应该继承core/base.py中的基础类：

```python
from ai_modular_blocks.core.base import BaseLLMProvider
from ai_modular_blocks.core.types import LLMConfig

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # 初始化OpenAI客户端
    
    async def _chat_completion_impl(self, ...):
        # 具体实现逻辑
        pass
```

### 2. 配置管理
每个Provider都有对应的配置类：

```python
# 使用配置
config = LLMConfig(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
    timeout=30.0,
    max_retries=3
)

provider = OpenAIProvider(config)
```

### 3. 错误处理
统一的错误处理和重试机制：

```python
from ai_modular_blocks.core.exceptions import (
    AuthenticationException,
    RateLimitException,
    TimeoutException
)

# Provider内部应该将第三方异常转换为框架异常
try:
    response = await openai_client.chat.completions.create(...)
except openai.AuthenticationError as e:
    raise AuthenticationException(str(e), provider_name="OpenAI")
```

## 📖 使用示例

### LLM Provider使用
```python
from ai_modular_blocks.providers.llm import OpenAIProvider
from ai_modular_blocks.core.types import LLMConfig, ChatMessage

# 配置和初始化
config = LLMConfig(api_key="your-api-key")
llm = OpenAIProvider(config)
await llm.initialize()

# 使用
messages = [ChatMessage(role="user", content="Hello!")]
response = await llm.chat_completion(
    messages=messages,
    model="gpt-3.5-turbo"
)

print(response.content)
```

### Vector Store使用
```python
from ai_modular_blocks.providers.vectorstores import PineconeProvider
from ai_modular_blocks.core.types import VectorStoreConfig, VectorDocument

# 配置和初始化
config = VectorStoreConfig(
    api_key="your-pinecone-key",
    index_name="my-index",
    dimension=1536
)
vector_store = PineconeProvider(config)
await vector_store.initialize()

# 存储文档
documents = [
    VectorDocument(
        id="doc1",
        content="Some text content",
        metadata={"source": "example"},
        embedding=[0.1, 0.2, ...]  # 1536维向量
    )
]

result = await vector_store.upsert(documents)
```

### Tool Provider使用
```python
from ai_modular_blocks.providers.tools import BuiltinToolProvider
from ai_modular_blocks.core.types import ToolCall

# 初始化工具提供商
tools = BuiltinToolProvider()
await tools.initialize()

# 执行工具
tool_call = ToolCall(
    id="call_1",
    name="calculator",
    arguments={"expression": "2 + 2"}
)

result = await tools.execute_tool(tool_call)
print(result.content)  # "4"
```

## 🚀 扩展指南

### 添加新的LLM Provider
1. 在`llm/`目录创建新文件
2. 继承`BaseLLMProvider`或`EnhancedLLMProvider`
3. 实现所有抽象方法
4. 在`llm/__init__.py`中注册

```python
# providers/llm/custom_llm.py
from ai_modular_blocks.core.base import BaseLLMProvider

class CustomLLMProvider(BaseLLMProvider):
    async def _chat_completion_impl(self, ...):
        # 自定义实现
        pass
```

### 添加新的工具
1. 在`tools/`对应分类目录中创建工具
2. 实现工具函数和定义
3. 注册到工具提供商

```python
# providers/tools/builtin/weather.py
from ai_modular_blocks.core.types import ToolDefinition, ToolParameter

def get_weather_tool_definition() -> ToolDefinition:
    return ToolDefinition(
        name="get_weather",
        description="Get current weather",
        parameters=[
            ToolParameter(
                name="location",
                type="string",
                description="City name",
                required=True
            )
        ]
    )

async def get_weather(location: str) -> str:
    # 实现天气查询逻辑
    return f"Weather in {location}: Sunny, 25°C"
```

## 🎨 设计原则

### 1. Provider无关性
用户代码不应该依赖特定Provider的实现细节：

```python
# ✅ 好的设计 - 依赖接口
llm: LLMProvider = get_llm_provider(config)
response = await llm.chat_completion(messages, model)

# ❌ 坏的设计 - 依赖具体实现
openai_llm = OpenAIProvider(config)
response = await openai_llm.openai_specific_method()  # 特定方法！
```

### 2. 配置驱动
所有Provider行为都应该通过配置控制：

```python
# 通过配置切换Provider
if config.provider_type == "openai":
    llm = OpenAIProvider(config.llm)
elif config.provider_type == "anthropic":
    llm = AnthropicProvider(config.llm)
```

### 3. 渐进式增强
支持基础功能和增强功能的分层实现：

```python
# 基础功能
if isinstance(llm, LLMProvider):
    response = await llm.chat_completion(messages, model)

# 增强功能
if isinstance(llm, EnhancedLLMProvider):
    response = await llm.chat_completion_with_tools(
        messages, tools, model
    )
```

## 🔍 测试策略

每个Provider都应该有：
- **单元测试** - 测试具体实现逻辑
- **集成测试** - 测试与第三方服务的集成
- **Mock测试** - 提供测试用的Mock实现
- **性能测试** - 验证并发和吞吐量表现

## 🎯 质量标准

- **接口一致性** - 严格遵循core/interfaces/定义
- **错误处理** - 统一的异常类型和错误信息
- **日志记录** - 详细的操作日志和性能指标
- **文档完整** - 每个Provider都有使用示例和配置说明
- **向后兼容** - 新版本不破坏现有API
