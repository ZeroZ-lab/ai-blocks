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

### `huggingface.py` - HuggingFace模型
- **支持模型**: 开源LLM（Llama, Mistral等）
- **核心功能**: 本地推理、模型微调
- **特殊功能**: 自定义模型加载、GPU加速

### `local.py` - 本地部署模型
- **支持框架**: Ollama, vLLM, TGI
- **核心功能**: 私有部署、离线推理
- **特殊功能**: 资源控制、批量推理

### `mock.py` - 测试Mock实现
- **用途**: 单元测试、开发调试
- **功能**: 可预测响应、延迟模拟
- **配置**: 自定义响应内容和延迟

## 📖 使用示例

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

# 初始化提供商
llm = OpenAIProvider(config)
await llm.initialize()

# 基础聊天
messages = [ChatMessage(role="user", content="Hello, AI!")]
response = await llm.chat_completion(messages, model="gpt-3.5-turbo")

# Function Calling（如果支持）
if isinstance(llm, EnhancedLLMProvider):
    tools = [weather_tool_definition]
    response = await llm.chat_completion_with_tools(
        messages=messages,
        tools=tools,
        model="gpt-3.5-turbo"
    )
```

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
    # 具体实现
    pass

async def _get_available_models_impl(self):
    # 返回支持的模型列表
    pass
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

1. 创建新文件 `providers/llm/my_provider.py`
2. 实现`BaseLLMProvider`或`EnhancedLLMProvider` 
3. 在`__init__.py`中注册
4. 添加配置类和测试

```python
# my_provider.py
class MyLLMProvider(BaseLLMProvider):
    async def _chat_completion_impl(self, messages, model, **kwargs):
        # 实现聊天逻辑
        pass
    
    async def _get_available_models_impl(self):
        return ["my-model-1", "my-model-2"]
```
