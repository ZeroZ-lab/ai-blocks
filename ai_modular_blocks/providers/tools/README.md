# Tool Providers

工具提供商实现

## 🎯 目录说明

本目录包含各种工具和Function Calling的具体实现，统一实现`ToolProvider`接口，为LLM提供外部能力扩展。

## 📁 工具分类

### `builtin/` - 内置工具
系统内置的基础工具，无需外部依赖：

```
builtin/
├── calculator.py      # 数学计算器
├── datetime.py        # 日期时间工具
├── text_processor.py  # 文本处理工具
├── unit_converter.py  # 单位转换工具
├── random_generator.py # 随机数生成器
└── string_utils.py    # 字符串工具
```

### `web/` - Web工具
与网络和Web服务相关的工具：

```
web/
├── search.py          # 网络搜索（Google, Bing）
├── web_scraper.py     # 网页内容抓取
├── url_analyzer.py    # URL分析和验证
├── api_client.py      # 通用API客户端
├── weather.py         # 天气查询
└── news.py           # 新闻获取
```

### `filesystem/` - 文件系统工具
文件和目录操作工具：

```
filesystem/
├── file_ops.py        # 文件读写操作
├── directory_ops.py   # 目录操作
├── file_search.py     # 文件搜索
├── image_processor.py # 图像处理
└── pdf_processor.py   # PDF处理
```

### `database/` - 数据库工具
数据库查询和操作工具：

```
database/
├── sql_executor.py    # SQL查询执行
├── redis_ops.py       # Redis操作
├── mongodb_ops.py     # MongoDB操作
└── csv_processor.py   # CSV数据处理
```

### `custom/` - 自定义工具框架
用户自定义工具的框架和示例：

```
custom/
├── tool_template.py   # 工具模板
├── decorator_tools.py # 装饰器工具
├── plugin_manager.py  # 插件管理器
└── examples/          # 自定义工具示例
```

## 📖 使用示例

### 基础工具使用
```python
from ai_modular_blocks.providers.tools import BuiltinToolProvider
from ai_modular_blocks.core.types import ToolCall

# 初始化内置工具提供商
tools = BuiltinToolProvider()
await tools.initialize()

# 获取可用工具
available_tools = await tools.get_available_tools()
print(f"可用工具: {[tool.name for tool in available_tools]}")

# 执行计算器工具
calc_call = ToolCall(
    id="call_1",
    name="calculator",
    arguments={"expression": "2 + 3 * 4"}
)

result = await tools.execute_tool(calc_call)
print(f"计算结果: {result.content}")  # "14"
```

### 与LLM集成使用
```python
from ai_modular_blocks.providers.llm import OpenAIProvider
from ai_modular_blocks.providers.tools import WebToolProvider

# 初始化LLM和工具
llm = OpenAIProvider(llm_config)
web_tools = WebToolProvider(web_config)

await llm.initialize()
await web_tools.initialize()

# 获取工具定义
tools = await web_tools.get_available_tools()

# LLM聊天（带工具）
if isinstance(llm, EnhancedLLMProvider):
    messages = [ChatMessage(role="user", content="今天北京天气怎么样？")]
    
    response = await llm.chat_completion_with_tools(
        messages=messages,
        tools=tools,
        model="gpt-3.5-turbo"
    )
    
    # 处理工具调用
    if response.tool_calls:
        tool_results = await web_tools.execute_tools_parallel(response.tool_calls)
        
        for result in tool_results:
            print(f"工具执行结果: {result.content}")
```

### 自定义工具开发
```python
from ai_modular_blocks.core.types import ToolDefinition, ToolParameter, ToolParameterType
from ai_modular_blocks.providers.tools.custom import CustomToolProvider

class MyCustomTools(CustomToolProvider):
    def __init__(self):
        super().__init__()
        self.register_custom_tools()
    
    def register_custom_tools(self):
        """注册自定义工具"""
        
        # 邮件发送工具
        email_tool = ToolDefinition(
            name="send_email",
            description="发送邮件给指定收件人",
            parameters=[
                ToolParameter(
                    name="to",
                    type=ToolParameterType.STRING,
                    description="收件人邮箱地址",
                    required=True
                ),
                ToolParameter(
                    name="subject", 
                    type=ToolParameterType.STRING,
                    description="邮件主题",
                    required=True
                ),
                ToolParameter(
                    name="body",
                    type=ToolParameterType.STRING, 
                    description="邮件正文",
                    required=True
                )
            ]
        )
        
        self.register_tool(email_tool, self.send_email_handler)
    
    async def send_email_handler(self, to: str, subject: str, body: str) -> str:
        """邮件发送处理器"""
        try:
            # 实际的邮件发送逻辑
            await self.email_client.send(
                to=to,
                subject=subject,
                body=body
            )
            return f"邮件已成功发送到 {to}"
        except Exception as e:
            return f"邮件发送失败: {str(e)}"
```

## 🔧 工具开发指南

### 基础工具结构
```python
from ai_modular_blocks.core.types import ToolDefinition, ToolParameter, ToolParameterType
import json

def create_calculator_tool() -> ToolDefinition:
    """创建计算器工具定义"""
    return ToolDefinition(
        name="calculator",
        description="执行数学计算表达式",
        parameters=[
            ToolParameter(
                name="expression",
                type=ToolParameterType.STRING,
                description="要计算的数学表达式，如 '2+3*4'",
                required=True
            )
        ],
        metadata={
            "category": "math",
            "safe": True,
            "timeout": 5
        }
    )

async def calculator_handler(expression: str) -> str:
    """计算器工具处理函数"""
    try:
        # 安全的表达式计算
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"
```

### 工具提供商实现
```python
from ai_modular_blocks.core.base import BaseProvider
from ai_modular_blocks.core.interfaces import ToolProvider

class MyToolProvider(BaseProvider, ToolProvider):
    def __init__(self, config):
        super().__init__(config, "tools")
        self.tools = {}
        self.handlers = {}
    
    async def register_tool(self, tool: ToolDefinition) -> bool:
        """注册工具"""
        self.tools[tool.name] = tool
        return True
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """执行工具调用"""
        tool_name = tool_call.name
        
        if tool_name not in self.handlers:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"未知工具: {tool_name}",
                success=False,
                error="TOOL_NOT_FOUND"
            )
        
        try:
            handler = self.handlers[tool_name]
            result_content = await handler(**tool_call.arguments)
            
            return ToolResult(
                tool_call_id=tool_call.id,
                content=result_content,
                success=True
            )
            
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"工具执行失败: {str(e)}",
                success=False,
                error=str(e)
            )
```

### 并行工具执行
```python
import asyncio

async def execute_tools_parallel(self, tool_calls: ToolCallList) -> ToolResultList:
    """并行执行多个工具调用"""
    # 限制并发数避免资源耗尽
    semaphore = asyncio.Semaphore(5)
    
    async def execute_with_semaphore(tool_call):
        async with semaphore:
            return await self.execute_tool(tool_call)
    
    # 并发执行所有工具调用
    tasks = [execute_with_semaphore(call) for call in tool_calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常结果
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_result = ToolResult(
                tool_call_id=tool_calls[i].id,
                content=f"工具执行异常: {str(result)}",
                success=False,
                error=str(result)
            )
            final_results.append(error_result)
        else:
            final_results.append(result)
    
    return final_results
```

## 🛡️ 安全考虑

### 工具安全等级
```python
class ToolSecurityLevel(Enum):
    SAFE = "safe"           # 安全工具，无副作用
    READ_ONLY = "read_only" # 只读操作
    WRITE = "write"         # 写操作，需要权限
    DANGEROUS = "dangerous" # 危险操作，需要确认

class SecureToolProvider(ToolProvider):
    def __init__(self, config, security_policy):
        super().__init__(config)
        self.security_policy = security_policy
    
    async def validate_tool_call(self, tool_call: ToolCall) -> bool:
        """验证工具调用安全性"""
        tool = self.tools.get(tool_call.name)
        if not tool:
            return False
        
        security_level = tool.metadata.get("security_level", ToolSecurityLevel.SAFE)
        
        # 根据安全策略验证
        if security_level == ToolSecurityLevel.DANGEROUS:
            return await self.security_policy.confirm_dangerous_operation(tool_call)
        
        return True
```

### 输入参数验证
```python
def validate_tool_parameters(tool: ToolDefinition, arguments: Dict[str, Any]) -> bool:
    """验证工具参数"""
    for param in tool.parameters:
        if param.required and param.name not in arguments:
            raise ValidationException(f"缺少必需参数: {param.name}")
        
        if param.name in arguments:
            value = arguments[param.name]
            
            # 类型验证
            if not validate_parameter_type(value, param.type):
                raise ValidationException(f"参数 {param.name} 类型错误")
            
            # 枚举值验证
            if param.enum and value not in param.enum:
                raise ValidationException(f"参数 {param.name} 值必须在 {param.enum} 中")
    
    return True
```

## 🚀 性能优化

### 工具缓存
```python
class CachedToolProvider(ToolProvider):
    def __init__(self, config, cache_provider):
        super().__init__(config)
        self.cache = cache_provider
    
    async def execute_tool_with_cache(self, tool_call: ToolCall) -> ToolResult:
        """带缓存的工具执行"""
        # 生成缓存键
        cache_key = self.generate_cache_key(tool_call)
        
        # 尝试从缓存获取
        cached_result = await self.cache.get(cache_key)
        if cached_result and self.is_cacheable_tool(tool_call.name):
            return ToolResult.from_dict(cached_result)
        
        # 执行工具
        result = await self.execute_tool(tool_call)
        
        # 缓存成功结果
        if result.success and self.is_cacheable_tool(tool_call.name):
            await self.cache.set(
                cache_key, 
                result.to_dict(), 
                ttl=self.get_cache_ttl(tool_call.name)
            )
        
        return result
    
    def is_cacheable_tool(self, tool_name: str) -> bool:
        """判断工具是否可缓存"""
        # 只有无副作用的工具才能缓存
        cacheable_tools = {"calculator", "unit_converter", "text_processor"}
        return tool_name in cacheable_tools
```

### 超时控制
```python
import asyncio

async def execute_tool_with_timeout(self, tool_call: ToolCall, timeout: float = 30.0) -> ToolResult:
    """带超时控制的工具执行"""
    try:
        result = await asyncio.wait_for(
            self.execute_tool(tool_call),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return ToolResult(
            tool_call_id=tool_call.id,
            content=f"工具执行超时 ({timeout}秒)",
            success=False,
            error="TIMEOUT"
        )
```

## 🧪 工具测试

### 单元测试示例
```python
import pytest
from ai_modular_blocks.providers.tools.builtin import CalculatorTool

@pytest.mark.asyncio
async def test_calculator_tool():
    """测试计算器工具"""
    tool = CalculatorTool()
    
    # 测试正常计算
    result = await tool.execute("2 + 3 * 4")
    assert result == "14"
    
    # 测试错误表达式
    result = await tool.execute("2 + + 3")
    assert "错误" in result
    
    # 测试安全性（不允许危险操作）
    result = await tool.execute("__import__('os').system('ls')")
    assert "错误" in result
```

### 集成测试示例
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_llm_integration(llm_provider, tool_provider):
    """测试工具与LLM的集成"""
    # 注册工具
    calc_tool = create_calculator_tool()
    await tool_provider.register_tool(calc_tool)
    
    # 获取工具列表
    tools = await tool_provider.get_available_tools()
    assert len(tools) > 0
    
    # LLM调用工具
    messages = [ChatMessage(role="user", content="计算 15 * 23")]
    response = await llm_provider.chat_completion_with_tools(
        messages=messages,
        tools=tools
    )
    
    # 验证工具被调用
    assert response.tool_calls is not None
    assert len(response.tool_calls) > 0
    
    # 执行工具
    tool_results = await tool_provider.execute_tools_parallel(response.tool_calls)
    assert tool_results[0].content == "345"
```

## 🎯 最佳实践

1. **工具设计** - 每个工具只做一件事，保持简单
2. **参数验证** - 严格验证所有输入参数
3. **错误处理** - 优雅处理各种异常情况
4. **安全考虑** - 实施适当的安全控制和权限管理
5. **性能优化** - 使用缓存和并发提高效率
6. **文档完整** - 为每个工具提供清晰的描述和示例
7. **测试覆盖** - 全面测试工具的功能和边界情况

## 🔍 故障排除

### 常见问题
- **工具未找到**: 检查工具是否正确注册
- **参数错误**: 验证参数类型和必需性
- **执行超时**: 调整超时设置或优化工具实现
- **权限错误**: 检查安全策略和工具权限配置
- **并发问题**: 合理设置并发限制和资源控制
