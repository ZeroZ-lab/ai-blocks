"""
用户完全自由的实现方式 - 无框架束缚

展示用户如何完全按照自己的方式实现，而不受框架抽象限制。
就像React一样，框架提供最小的核心，其余的都是用户的创作自由。
"""

import asyncio
import os

# 最小化导入 - 只要核心功能
from ai_modular_blocks.minimal import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations


class MyOwnAgent:
    """
    用户完全自定义的Agent类 - 无需继承任何框架类
    这就是纯Python，没有任何框架抽象
    """
    
    def __init__(self, name: str):
        self.name = name
        self.llm = create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
        
        # 选择自己需要的工具 - 完全自主选择
        self.calc = Calculator()
        self.files = FileOperations()
        
        # 用户自定义的状态管理
        self.conversation = []
        self.context = {}
    
    async def chat(self, message: str) -> str:
        """用户定义的对话方法 - 想怎么实现就怎么实现"""
        
        # 添加到对话历史 - 用户自己的格式
        self.conversation.append({"role": "user", "content": message})
        
        # 检查是否需要计算 - 用户自己的逻辑
        if "计算" in message or "算" in message:
            return await self._handle_calculation(message)
        
        # 检查是否需要文件操作 - 用户自己的逻辑  
        if "读文件" in message or "写文件" in message:
            return await self._handle_file_ops(message)
        
        # 普通对话 - 直接调用LLM
        response = await self.llm.generate(message)
        answer = response["content"]
        
        # 记录回复 - 用户自己的格式
        self.conversation.append({"role": "assistant", "content": answer})
        
        return answer
    
    async def _handle_calculation(self, message: str) -> str:
        """用户自己实现的计算处理逻辑"""
        # 简单的表达式提取 - 用户可以用任何方法
        import re
        
        # 寻找数学表达式
        patterns = [
            r'(\d+[\+\-\*/\(\)\s\d]*\d+)',  # 基本数学表达式
            r'(\d+)',  # 单个数字
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message)
            if matches:
                expression = matches[0].replace(' ', '')
                result = self.calc.calculate(expression)
                
                if result["success"]:
                    return f"计算结果：{expression} = {result['result']}"
                else:
                    return f"计算出错：{result['error']}"
        
        return "没有找到可以计算的表达式"
    
    async def _handle_file_ops(self, message: str) -> str:
        """用户自己实现的文件操作逻辑"""
        if "读文件" in message:
            # 简单提取文件名 - 用户可以用更复杂的NLP
            import re
            file_match = re.search(r'读文件\s*([^\s]+)', message)
            if file_match:
                filename = file_match.group(1)
                result = self.files.read_file(filename)
                
                if result["success"]:
                    return f"文件内容（前200字符）：\n{result['content'][:200]}..."
                else:
                    return f"读取文件失败：{result['error']}"
        
        return "文件操作格式不正确"


# 另一种完全不同的实现方式
class AnotherUserAgent:
    """
    另一个用户的完全不同实现方式
    展示框架不限制用户的创意
    """
    
    def __init__(self):
        # 用户可能选择不同的LLM
        self.llm = create_llm("openai", 
                             api_key=os.getenv("OPENAI_API_KEY"),
                             model="gpt-4",
                             temperature=0.9)
        
        # 用户可能有自己的工具组合
        self.tools = {"calc": Calculator()}
        
        # 完全不同的状态管理
        self.memory = {"short": [], "long": {}}
    
    async def think_and_respond(self, input_text: str):
        """用户完全自定义的处理流程"""
        
        # 用户自己的思考步骤
        thinking = await self.llm.generate(f"分析这个问题：{input_text}")
        
        # 用户自己的行动决策
        if "需要计算" in thinking["content"]:
            calc_result = self.tools["calc"].calculate("2+2")  # 示例
            final_prompt = f"基于计算结果 {calc_result['result']}，回答：{input_text}"
        else:
            final_prompt = input_text
        
        # 最终回复
        response = await self.llm.generate(final_prompt)
        
        return {
            "thinking": thinking["content"],
            "response": response["content"],
            "used_tools": "calc" if "需要计算" in thinking["content"] else None
        }


# 函数式的实现方式 - 用户可能更喜欢函数式
async def simple_chat_function(message: str) -> str:
    """
    函数式实现 - 完全不需要类
    """
    llm = create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
    response = await llm.generate(message)
    return response["content"]


# 用户的自定义工具
class MyCustomTool:
    """用户完全自定义的工具"""
    
    def __init__(self):
        self.data = {"users": ["Alice", "Bob", "Charlie"]}
    
    def search_users(self, query: str):
        """用户自己实现的搜索逻辑"""
        results = [user for user in self.data["users"] if query.lower() in user.lower()]
        return {"results": results, "count": len(results)}


async def demonstrate_freedom():
    """演示用户的完全自由度"""
    
    print("=== 用户实现方式1：面向对象 ===")
    agent1 = MyOwnAgent("我的助手")
    
    response1 = await agent1.chat("你好！")
    print(f"回复: {response1}")
    
    response2 = await agent1.chat("帮我计算 2+3*4")
    print(f"回复: {response2}")
    
    print(f"对话历史条数: {len(agent1.conversation)}")
    
    print("\n=== 用户实现方式2：不同风格 ===")
    agent2 = AnotherUserAgent()
    
    result = await agent2.think_and_respond("什么是人工智能？")
    print(f"思考: {result['thinking'][:100]}...")
    print(f"回复: {result['response'][:100]}...")
    
    print("\n=== 用户实现方式3：函数式 ===")
    answer = await simple_chat_function("简单问好")
    print(f"函数式回复: {answer}")
    
    print("\n=== 用户自定义工具 ===")
    my_tool = MyCustomTool()
    search_result = my_tool.search_users("Ali")
    print(f"搜索结果: {search_result}")


async def main():
    """主函数"""
    print("AI Modular Blocks - 用户完全自由实现")
    print("=" * 50)
    print("框架只提供最小核心，用户可以完全按照自己的方式实现")
    print("就像React只提供createElement，其余都是JavaScript的自由发挥")
    print()
    
    try:
        await demonstrate_freedom()
    except Exception as e:
        print(f"演示出错: {e}")
        print("提示: 请确保设置了正确的API密钥")
    
    print("\n" + "=" * 50)
    print("核心理念：")
    print("- 框架语法极少，主要依赖Python语言特性")
    print("- 没有强制的抽象基类或复杂继承")  
    print("- 用户可以自由选择实现方式")
    print("- 每个工具都独立，可以单独使用")
    print("- 组合优于继承，自由度最大化")


if __name__ == "__main__":
    asyncio.run(main())