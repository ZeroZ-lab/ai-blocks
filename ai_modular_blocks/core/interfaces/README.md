# Interfaces Module

接口定义模块 - AI Modular Blocks的协议层

## 🎯 职责范围

定义系统中所有的抽象基类和接口协议，确保不同实现之间的兼容性和可替换性。

## 📁 文件组织

### `llm.py` - 大语言模型接口
定义LLM提供商的标准操作：

```python
LLMProvider         # 基础LLM接口（聊天、流式、模型列表）
EnhancedLLMProvider # 增强LLM接口（支持Function Calling）
```

**核心能力**: 聊天补全、流式响应、工具调用、健康检查

### `storage.py` - 存储服务接口
定义数据存储和检索的标准操作：

```python
VectorStore        # 向量存储接口（存储、搜索、删除）
EmbeddingProvider  # 嵌入服务接口（文本向量化）
```

**核心能力**: 向量相似性搜索、文档嵌入、批量操作

### `tools.py` - 工具系统接口
定义工具注册和执行的标准操作：

```python
ToolProvider       # 工具提供商接口（注册、执行、验证）
```

**核心能力**: 工具注册、并行执行、参数验证

### `mcp.py` - MCP协议接口
定义Model Context Protocol的标准操作：

```python
MCPProvider        # MCP提供商接口（连接、资源、工具）
```

**核心能力**: 协议连接、资源访问、变更订阅

### `utilities.py` - 工具类接口
定义系统工具组件的标准操作：

```python
DocumentProcessor  # 文档处理器接口
CacheProvider     # 缓存提供商接口
Middleware        # 中间件接口
Plugin            # 插件接口
```

**核心能力**: 文档处理、缓存管理、请求拦截、功能扩展

## 🏗️ 接口设计原则

### 1. 接口隔离原则 (ISP)
每个接口都专注于特定职责，避免臃肿的"上帝接口"：

```python
# ✅ 好的设计 - 职责单一
class LLMProvider(ABC):
    @abstractmethod
    async def chat_completion(...) -> LLMResponse: pass

class ToolProvider(ABC):
    @abstractmethod
    async def execute_tool(...) -> ToolResult: pass

# ❌ 坏的设计 - 职责混乱
class AIProvider(ABC):
    async def chat_completion(...): pass
    async def execute_tool(...): pass
    async def store_vector(...): pass  # 太多职责！
```

### 2. 里氏替换原则 (LSP)
任何接口的实现都可以无缝替换：

```python
# OpenAI和Anthropic的实现可以互换使用
llm: LLMProvider = OpenAIProvider(config)
llm: LLMProvider = AnthropicProvider(config)
```

### 3. 异步优先
所有I/O操作都是异步的，支持高并发：

```python
async def chat_completion(...) -> LLMResponse: pass
async def search(...) -> List[SearchResult]: pass
```

## 🔄 接口组合模式

通过组合不同接口实现复杂功能：

```python
class RAGSystem:
    def __init__(
        self,
        llm: LLMProvider,
        vector_store: VectorStore,
        embedding: EmbeddingProvider,
        tools: ToolProvider
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.embedding = embedding
        self.tools = tools
    
    async def enhanced_chat(self, query: str) -> str:
        # 1. 向量搜索相关文档
        query_embedding = await self.embedding.embed_text([query])
        docs = await self.vector_store.search(query_embedding[0])
        
        # 2. LLM生成回复（可能调用工具）
        if isinstance(self.llm, EnhancedLLMProvider):
            tools = await self.tools.get_available_tools()
            response = await self.llm.chat_completion_with_tools(
                messages=[ChatMessage(role="user", content=query)],
                tools=tools
            )
        else:
            response = await self.llm.chat_completion(
                messages=[ChatMessage(role="user", content=query)]
            )
        
        return response.content
```

## 📖 实现指南

### 基础Provider实现
```python
from ai_modular_blocks.core.interfaces import LLMProvider
from ai_modular_blocks.core.types import LLMResponse, MessageList

class MyLLMProvider(LLMProvider):
    async def chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        # 实现具体逻辑
        pass
    
    async def stream_chat_completion(self, ...):
        # 实现流式响应
        pass
    
    async def get_available_models(self) -> List[str]:
        # 返回支持的模型列表
        pass
    
    async def health_check(self) -> bool:
        # 健康检查逻辑
        pass
```

### 增强功能实现
```python
from ai_modular_blocks.core.interfaces import EnhancedLLMProvider

class MyEnhancedLLMProvider(EnhancedLLMProvider):
    # 继承基础LLM功能
    
    async def chat_completion_with_tools(
        self,
        messages: MessageList,
        tools: Optional[ToolList] = None,
        **kwargs
    ) -> EnhancedLLMResponse:
        # 实现Function Calling逻辑
        pass
```

## 🔧 最佳实践

### 1. 错误处理
```python
from ai_modular_blocks.core.exceptions import ProviderException

async def chat_completion(self, ...):
    try:
        # 实现逻辑
        pass
    except Exception as e:
        raise ProviderException(
            f"Chat completion failed: {str(e)}",
            provider_name=self.__class__.__name__
        ) from e
```

### 2. 参数验证
```python
from ai_modular_blocks.core.validators import InputValidator

async def chat_completion(self, messages: MessageList, ...):
    validated_messages = InputValidator.validate_message_list(messages)
    # 使用验证后的数据
```

### 3. 日志记录
```python
import logging

class MyProvider(LLMProvider):
    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def chat_completion(self, ...):
        self.logger.info(f"Processing chat completion with {len(messages)} messages")
```

## 🎨 设计哲学

> "Program to an interface, not an implementation." - Gang of Four

- **抽象即力量** - 接口定义了系统的能力边界
- **组合胜继承** - 通过接口组合构建复杂功能
- **契约编程** - 接口就是组件间的契约
- **扩展性优先** - 新功能通过新接口添加，不破坏现有接口

## 🚀 扩展路径

1. **新Provider类型** - 在对应文件中添加新接口
2. **接口增强** - 通过继承扩展现有接口功能
3. **组合模式** - 通过多接口组合实现复杂业务逻辑
4. **插件化** - 通过Plugin接口实现功能扩展
