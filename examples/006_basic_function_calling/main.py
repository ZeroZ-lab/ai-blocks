"""
006 - 基础函数调用示例

展示LLM如何调用外部函数：
- 用户自定义函数，无框架束缚
- 纯Python函数定义和调用
- 灵活的工具注册和执行机制
"""

import asyncio
import os
import json
from typing import Dict, Any, List, Callable
from datetime import datetime
from dotenv import load_dotenv

from ai_modular_blocks import create_llm, ToolDefinition, ToolCall, ToolResult

load_dotenv()


class SimpleToolRegistry:
    """用户自定义的工具注册表 - 不需要继承任何框架类！"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_function(self, name: str, func: Callable, description: str, 
                         parameters: Dict[str, Any]):
        """注册一个Python函数作为工具"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        print(f"✅ 已注册工具: {name}")
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """获取所有工具的定义"""
        definitions = []
        for name, info in self.tools.items():
            definitions.append(ToolDefinition(
                name=name,
                description=info["description"],
                parameters=info["parameters"]
            ))
        return definitions
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """执行工具调用"""
        tool_name = tool_call.name
        
        if tool_name not in self.tools:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_name,
                error=f"工具 '{tool_name}' 不存在",
                success=False
            )
        
        try:
            func = self.tools[tool_name]["function"]
            
            # 调用用户的Python函数
            if asyncio.iscoroutinefunction(func):
                result = await func(**tool_call.arguments)
            else:
                result = func(**tool_call.arguments)
            
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_name,
                result=result,
                success=True
            )
            
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_name,
                error=f"工具执行失败: {str(e)}",
                success=False
            )


# 用户自定义的工具函数 - 纯Python函数！

def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
    """获取当前时间"""
    now = datetime.now()
    return {
        "current_time": now.strftime(format),
        "timestamp": now.timestamp(),
        "timezone": "local"
    }


def calculate_math(expression: str) -> Dict[str, Any]:
    """安全地计算数学表达式"""
    try:
        # 安全的数学计算（限制可用函数）
        allowed_names = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "pow": pow, "sum": sum
        }
        
        import math
        allowed_names.update({
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "pi": math.pi, "e": math.e
        })
        
        result = eval(expression, allowed_names)
        return {
            "result": result,
            "expression": expression,
            "type": type(result).__name__
        }
    except Exception as e:
        return {
            "error": str(e),
            "expression": expression
        }


def generate_password(length: int = 12, include_symbols: bool = True) -> Dict[str, Any]:
    """生成随机密码"""
    import random
    import string
    
    if length < 4 or length > 50:
        return {"error": "密码长度必须在4-50之符之间"}
    
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    
    return {
        "password": password,
        "length": len(password),
        "has_symbols": include_symbols,
        "strength": "strong" if length >= 12 and include_symbols else "medium"
    }


def get_word_count(text: str) -> Dict[str, Any]:
    """统计文本信息"""
    words = text.split()
    chars_no_space = len(text.replace(' ', ''))
    lines = text.count('\n') + 1
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "character_count_no_spaces": chars_no_space,
        "line_count": lines,
        "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
    }


class FunctionCallingBot:
    """带函数调用功能的聊天机器人"""
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(
            provider,
            api_key=os.getenv(f"{provider.upper()}_API_KEY"),
            temperature=0.7
        )
        
        self.tool_registry = SimpleToolRegistry()
        self._register_default_tools()
        self.provider = provider
    
    def _register_default_tools(self):
        """注册默认工具"""
        
        # 注册时间工具
        self.tool_registry.register_function(
            "get_current_time",
            get_current_time,
            "获取当前日期和时间",
            {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "时间格式字符串，默认为 '%Y-%m-%d %H:%M:%S'",
                        "default": "%Y-%m-%d %H:%M:%S"
                    }
                },
                "required": []
            }
        )
        
        # 注册数学计算工具
        self.tool_registry.register_function(
            "calculate_math",
            calculate_math,
            "安全地计算数学表达式，支持基本运算和数学函数",
            {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '2+3*4' 或 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        )
        
        # 注册密码生成工具
        self.tool_registry.register_function(
            "generate_password", 
            generate_password,
            "生成安全的随机密码",
            {
                "type": "object",
                "properties": {
                    "length": {
                        "type": "integer",
                        "description": "密码长度，4-50之间",
                        "default": 12
                    },
                    "include_symbols": {
                        "type": "boolean", 
                        "description": "是否包含特殊符号",
                        "default": True
                    }
                },
                "required": []
            }
        )
        
        # 注册文本统计工具
        self.tool_registry.register_function(
            "get_word_count",
            get_word_count,
            "统计文本的字数、字符数、行数等信息",
            {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要统计的文本内容"
                    }
                },
                "required": ["text"]
            }
        )
    
    async def chat_with_tools(self, message: str) -> str:
        """带工具调用的聊天"""
        print(f"👤 用户: {message}")
        
        try:
            # 获取工具定义
            tools = self.tool_registry.get_tool_definitions()
            
            # 调用LLM（假设支持工具调用）
            # 这里需要根据实际的LLM接口调整
            response = await self._call_llm_with_tools(message, tools)
            
            return response
            
        except Exception as e:
            return f"❌ 对话失败: {str(e)}"
    
    async def _call_llm_with_tools(self, message: str, tools: List[ToolDefinition]) -> str:
        """调用支持工具的LLM（简化版实现）"""
        
        # 构建系统提示
        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(
                f"- {tool.name}: {tool.description}"
            )
        
        system_prompt = f"""你是一个有用的助手，可以调用以下工具：

{chr(10).join(tool_descriptions)}

如果用户的问题需要使用工具，请按以下格式回复：
TOOL_CALL: tool_name(param1="value1", param2="value2")

如果不需要工具，直接回复用户。"""
        
        # 调用LLM
        full_prompt = f"{system_prompt}\n\n用户问题: {message}"
        response = await self.llm.generate(full_prompt)
        answer = response["content"]
        
        # 检查是否需要工具调用
        if "TOOL_CALL:" in answer:
            return await self._handle_tool_call(answer, message)
        else:
            return answer
    
    async def _handle_tool_call(self, llm_response: str, original_message: str) -> str:
        """处理工具调用（简化版解析）"""
        try:
            # 简化的工具调用解析
            import re
            
            # 寻找工具调用模式
            pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
            match = re.search(pattern, llm_response)
            
            if not match:
                return llm_response
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # 简化的参数解析（实际应用中需要更健壮的解析）
            params = {}
            if params_str.strip():
                # 基础的参数解析
                param_pairs = params_str.split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        # 尝试转换类型
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        params[key] = value
            
            print(f"🔧 调用工具: {tool_name}({params})")
            
            # 创建工具调用
            tool_call = ToolCall(
                id=f"call_{datetime.now().timestamp()}",
                name=tool_name,
                arguments=params
            )
            
            # 执行工具
            result = await self.tool_registry.execute_tool(tool_call)
            
            if result.success:
                print(f"✅ 工具执行成功: {result.result}")
                
                # 将结果返回给LLM进行最终回复
                final_prompt = f"""用户问题: {original_message}

我调用了工具 {tool_name}，得到结果：
{json.dumps(result.result, ensure_ascii=False, indent=2)}

请基于这个结果给用户一个友好的回复。"""
                
                final_response = await self.llm.generate(final_prompt)
                return final_response["content"]
            else:
                return f"❌ 工具调用失败: {result.error}"
                
        except Exception as e:
            print(f"❌ 工具调用处理失败: {e}")
            return llm_response


async def demo_function_calling():
    """演示函数调用功能"""
    print("🚀 基础函数调用演示")
    print("=" * 50)
    
    # 尝试创建聊天机器人
    providers = ["openai", "deepseek", "anthropic"]
    bot = None
    
    for provider in providers:
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        if api_key:
            try:
                bot = FunctionCallingBot(provider)
                print(f"✅ 使用 {provider.title()} 提供商")
                break
            except Exception as e:
                print(f"⚠️  {provider} 初始化失败: {e}")
    
    if not bot:
        print("❌ 没有可用的API密钥")
        return
    
    # 显示可用工具
    tools = bot.tool_registry.get_tool_definitions()
    print(f"\n🔧 可用工具 ({len(tools)}个):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # 测试问题
    test_questions = [
        "现在几点了？",
        "帮我计算 25 * 4 + sqrt(16)",
        "生成一个15位的安全密码",
        "统计这段文本的信息：'Hello world! This is a test message with multiple words.'"
    ]
    
    print(f"\n🎯 测试函数调用功能:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n【测试 {i}】")
        response = await bot.chat_with_tools(question)
        print(f"🤖 助手: {response}")
        
        if i < len(test_questions):
            await asyncio.sleep(1)


async def main():
    """主函数"""
    print("🌟 AI Modular Blocks - 基础函数调用")
    print("展示LLM调用用户自定义的Python函数")
    print()
    
    await demo_function_calling()
    
    print("\n🎯 核心特点:")
    print("- 用户定义纯Python函数，无需特殊装饰器")
    print("- 灵活的工具注册和执行机制")
    print("- 支持异步和同步函数调用")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")