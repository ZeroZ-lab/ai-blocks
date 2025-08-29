# Types Module

类型定义模块 - AI Modular Blocks的数据结构层

## 🎯 职责范围

定义系统中所有的数据类型、数据类和类型别名，确保类型安全和代码清晰度。

## 📁 文件组织

### `basic.py` - 基础类型
核心业务数据结构，系统的基石：

```python
ChatMessage      # 聊天消息格式
LLMResponse      # LLM提供商响应格式
VectorDocument   # 向量文档表示
SearchResult     # 向量搜索结果
ContentType      # 内容类型枚举
ProcessingConfig # 处理配置
```

**设计原则**: 简单、通用、无依赖

### `tools.py` - 工具和Function Calling类型
现代AI应用的核心能力：

```python
ToolDefinition       # 工具定义（OpenAI兼容格式）
ToolCall            # 工具调用请求
ToolResult          # 工具执行结果
EnhancedLLMResponse # 支持工具调用的LLM响应
FunctionCallMessage # 支持函数调用的消息
```

**设计原则**: 遵循OpenAI标准，支持流式和批量操作

### `mcp.py` - Model Context Protocol类型
标准化的AI模型-工具通信协议：

```python
MCPResource     # MCP资源定义
MCPContext      # MCP上下文信息
MCPResourceType # MCP资源类型枚举
```

**设计原则**: 符合MCP协议规范，支持多种资源类型

### `config.py` - 配置类型
各种Provider和系统的配置结构：

```python
ProviderConfig   # 基础Provider配置
LLMConfig       # LLM提供商配置
VectorStoreConfig # 向量存储配置
EmbeddingConfig  # 嵌入服务配置
ToolConfig      # 工具系统配置
MCPConfig       # MCP协议配置
```

**设计原则**: 类型安全的配置管理，支持验证和序列化

## 🔗 依赖关系

```
basic.py         # 无依赖 - 系统基石
    ↑
config.py        # 依赖basic.py（继承ProviderConfig）
    ↑
tools.py         # 依赖basic.py（继承LLMResponse, ChatMessage）
    ↑
mcp.py          # 依赖tools.py（引用ToolDefinition）
```

## 📖 使用示例

### 基础类型使用
```python
from ai_modular_blocks.core.types import ChatMessage, LLMResponse

message = ChatMessage(
    role="user",
    content="Hello, AI!"
)

response = LLMResponse(
    content="Hello! How can I help you?",
    model="gpt-3.5-turbo",
    usage={"prompt_tokens": 10, "completion_tokens": 8},
    created_at=datetime.now(),
    finish_reason="stop"
)
```

### 工具类型使用
```python
from ai_modular_blocks.core.types import ToolDefinition, ToolParameter, ToolParameterType

tool = ToolDefinition(
    name="get_weather",
    description="Get current weather for a location",
    parameters=[
        ToolParameter(
            name="location",
            type=ToolParameterType.STRING,
            description="City name",
            required=True
        )
    ]
)
```

### 类型别名
```python
from ai_modular_blocks.core.types import MessageList, ToolList

# 使用类型别名提高代码可读性
def process_conversation(messages: MessageList, tools: ToolList) -> str:
    # 处理逻辑
    pass
```

## ⚡ 性能考虑

- **使用dataclass** - 高效的数据容器
- **类型别名** - 零运行时开销的类型提示
- **可选字段** - 减少内存占用和网络传输
- **枚举类型** - 类型安全的常量定义

## 🛡️ 类型安全

所有类型都经过精心设计，确保：
- **运行时类型检查** - 通过validators.py验证
- **静态类型检查** - 完整的类型提示支持
- **向后兼容性** - 新字段使用Optional
- **序列化支持** - 支持JSON和其他格式

## 🎨 设计哲学

> "Data structures, not algorithms, are central to programming." - Rob Pike

- **数据为王** - 好的数据结构是好程序的基础
- **类型即文档** - 类型定义就是最好的API文档
- **简单优于复杂** - 宁可多几个简单类型，也不要一个复杂类型
