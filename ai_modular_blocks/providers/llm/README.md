# LLM Providers

大语言模型提供商实现

## 🎯 目录说明

本目录包含各种大语言模型服务商的具体实现，统一实现`LLMProvider`和`EnhancedLLMProvider`接口。

## 📁 提供商列表

### `openai.py` - OpenAI GPT系列
- **支持模型**: GPT-3.5, GPT-4, GPT-4 Turbo
- **核心功能**: 聊天补全、Function Calling、流式响应
- **特殊功能**: 视觉模型支持、JSON模式

### `anthropic.py` - Anthropic Claude系列  
- **支持模型**: Claude-3 Haiku, Sonnet, Opus
- **核心功能**: 长上下文处理、安全对话
- **特殊功能**: 系统提示优化、思维链推理

### `deepseek_provider.py` - DeepSeek AI模型 ✅
- **支持模型**: DeepSeek-V3, DeepSeek-Chat, DeepSeek-Coder, DeepSeek-Reasoner
- **核心功能**: 代码生成、推理能力、中英文对话
- **特殊功能**: OpenAI API兼容、高性能推理、128K上下文
- **API格式**: OpenAI兼容，使用openai包作为依赖

### 🚧 计划中的Provider

以下Provider正在规划中，欢迎贡献：

#### `huggingface_provider.py` - HuggingFace模型
- **支持模型**: 开源LLM（Llama, Mistral等）
- **核心功能**: 本地推理、模型微调
- **特殊功能**: 自定义模型加载、GPU加速

#### `local_provider.py` - 本地部署模型  
- **支持框架**: Ollama, vLLM, TGI
- **核心功能**: 私有部署、离线推理
- **特殊功能**: 资源控制、批量推理

#### `mock_provider.py` - 测试Mock实现
- **用途**: 单元测试、开发调试
- **功能**: 可预测响应、延迟模拟
- **配置**: 自定义响应内容和延迟

## 📖 使用示例

### OpenAI Provider
```python
from ai_modular_blocks.providers.llm import OpenAIProvider
from ai_modular_blocks.core.types import LLMConfig, ChatMessage

# 配置OpenAI
config = LLMConfig(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",  # 可选
    timeout=30.0,
    max_retries=3
)

# 创建提供商（自动初始化）
llm = OpenAIProvider(config)

# 基础聊天
messages = [ChatMessage(role="user", content="Hello, AI!")]
response = await llm.chat_completion(messages, model="gpt-3.5-turbo")
```

### DeepSeek Provider
```python
from ai_modular_blocks.providers.llm import DeepSeekProvider
from ai_modular_blocks.core.types import LLMConfig, ChatMessage

# 配置DeepSeek
config = LLMConfig(
    api_key="sk-...",  # DeepSeek API key
    base_url="https://api.deepseek.com/v1",  # 默认端点
    timeout=30.0,
    max_retries=3
)

# 创建DeepSeek提供商（自动初始化）
llm = DeepSeekProvider(config)

# DeepSeek聊天
messages = [ChatMessage(role="user", content="用Python写一个快速排序")]
response = await llm.chat_completion(messages, model="deepseek-coder")

# 流式响应
async for chunk in llm.stream_chat_completion(messages, model="deepseek-chat"):
    print(chunk.content, end="")
```

### 工厂模式使用
```python
from ai_modular_blocks.providers.llm.factory import LLMProviderFactory

# 列出可用提供商
providers = LLMProviderFactory.get_available_providers()
print(f"可用提供商: {providers}")  # ['openai', 'anthropic', 'deepseek']

# 创建DeepSeek provider
config = LLMConfig(api_key="sk-...")
llm = LLMProviderFactory.create_provider("deepseek", config)
```

## ⚡ 自动初始化特性

**重要改进**：所有provider现在支持自动初始化！

```python
# ✅ 新的使用方式 - 无需手动initialize
llm = DeepSeekProvider(config)
response = await llm.chat_completion(messages, model="deepseek-chat")  # 自动初始化

# ❌ 旧的使用方式 - 不再需要
llm = DeepSeekProvider(config)
await llm.initialize()  # 现在可以省略这一步
response = await llm.chat_completion(messages, model="deepseek-chat")
```

**技术实现**：
- 所有API调用方法（`chat_completion`、`stream_chat_completion`等）会自动检查并初始化client
- 使用基类的`initialize()`方法确保：
  - ✅ 重复初始化保护（只初始化一次）
  - ✅ 统一的错误处理和日志记录
  - ✅ 状态管理（`_initialized`标志）

## 🔧 实现指南

每个Provider都应该：

1. **继承基础类**
```python
from ai_modular_blocks.core.base import BaseLLMProvider

class MyLLMProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
```

2. **实现必需方法**
```python
async def _chat_completion_impl(self, messages, model, temperature, max_tokens, **kwargs):
    # 自动初始化检查（推荐模式）
    if not self.client:
        await self.initialize()
    
    # 具体API调用实现
    # ...
    pass

async def _get_available_models_impl(self):
    # 如果需要API调用，添加自动初始化
    if not self.client:
        await self.initialize()
    
    # 或者直接返回静态模型列表（如Anthropic）
    return self.get_supported_models()
```

3. **错误处理转换**
```python
try:
    # 调用第三方API
    response = await third_party_api.chat(...)
except ThirdPartyException as e:
    raise ProviderException(f"Chat failed: {e}", provider_name=self.provider_name)
```

## 🚀 扩展新Provider

参考DeepSeek provider的实现模式：

1. **创建Provider文件** `providers/llm/my_provider.py`
2. **实现基础接口** - 继承`BaseLLMProvider`
3. **添加工厂注册** - 在`factory.py`中添加发现逻辑
4. **更新导出** - 在`__init__.py`中添加导入
5. **编写测试** - 验证功能正确性

```python
# my_provider.py - 参考DeepSeek实现
class MyLLMProvider(BaseLLMProvider):
    DEFAULT_BASE_URL = "https://api.my-service.com/v1"
    SUPPORTED_MODELS = ["my-model-1", "my-model-2"]
    
    @classmethod
    def is_available(cls) -> bool:
        # 检查依赖可用性
        return True
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        return cls.SUPPORTED_MODELS.copy()
    
    async def _chat_completion_impl(self, messages, model, **kwargs):
        # 实现具体的聊天逻辑
        pass
    
    async def _get_available_models_impl(self):
        return self.SUPPORTED_MODELS.copy()
```
