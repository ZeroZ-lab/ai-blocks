"""
007 - 计算器工具集成示例

展示如何使用独立的计算器工具：
- 使用新架构的独立工具模块
- 纯Python组合，无框架抽象
- 用户可以自由选择和组合工具
"""

import asyncio
import os
from dotenv import load_dotenv

# 新架构：导入独立工具和最小核心
from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator

load_dotenv()


class MathAssistant:
    """用户自定义的数学助手 - 组合LLM和计算器工具"""
    
    def __init__(self, provider: str = "openai"):
        # 创建LLM
        self.llm = create_llm(
            provider,
            api_key=os.getenv(f"{provider.upper()}_API_KEY"),
            temperature=0.3  # 数学问题用较低温度
        )
        
        # 创建独立的计算器工具
        self.calculator = Calculator()
        self.provider = provider
    
    async def solve_math_problem(self, problem: str) -> str:
        """解决数学问题"""
        print(f"🧮 数学问题: {problem}")
        
        # 先让LLM分析问题
        analysis_prompt = f"""分析这个数学问题："{problem}"

请：
1. 识别需要计算的数学表达式
2. 如果需要计算，提取出可以直接计算的表达式
3. 如果不需要计算，说明这是概念性问题

返回格式：
- 类型：[计算题/概念题]  
- 表达式：[如果是计算题，写出表达式]
- 说明：[简短说明]"""
        
        try:
            analysis = await self.llm.generate(analysis_prompt)
            analysis_text = analysis["content"]
            
            print(f"🤔 分析结果: {analysis_text[:100]}...")
            
            # 检查是否需要计算
            if "计算题" in analysis_text and "表达式：" in analysis_text:
                return await self._handle_calculation_problem(problem, analysis_text)
            else:
                return await self._handle_concept_problem(problem)
                
        except Exception as e:
            return f"❌ 问题分析失败: {str(e)}"
    
    async def _handle_calculation_problem(self, problem: str, analysis: str) -> str:
        """处理计算题"""
        
        # 提取表达式（简化版）
        expressions = self._extract_expressions(analysis)
        
        if not expressions:
            # 让LLM再次尝试提取
            extract_prompt = f"""从这个数学问题中提取出可以计算的表达式："{problem}"

只返回数学表达式，例如：
- 2+3*4
- sqrt(25) + pow(2,3)
- (15-3)/4

表达式："""
            
            try:
                extract_result = await self.llm.generate(extract_prompt)
                expression_text = extract_result["content"].strip()
                
                # 清理提取的表达式
                import re
                # 寻找数学表达式模式
                pattern = r'[0-9+\-*/(). ]+|sqrt\([^)]+\)|pow\([^)]+\)'
                matches = re.findall(pattern, expression_text)
                if matches:
                    expressions = [matches[0].strip()]
            except:
                pass
        
        if expressions:
            print(f"🔢 识别的表达式: {expressions}")
            
            results = []
            for expr in expressions:
                calc_result = self.calculator.calculate(expr)
                results.append(calc_result)
                
                if calc_result["success"]:
                    print(f"✅ {expr} = {calc_result['result']}")
                else:
                    print(f"❌ {expr} 计算失败: {calc_result.get('error')}")
            
            # 让LLM基于计算结果生成最终回复
            results_text = "\n".join([
                f"{r['expression']} = {r.get('result', '计算失败')}" 
                for r in results
            ])
            
            final_prompt = f"""用户问题: {problem}

计算结果:
{results_text}

请基于这些计算结果给出完整、友好的回答。"""
            
            final_response = await self.llm.generate(final_prompt)
            return final_response["content"]
        
        else:
            # 无法提取表达式，让LLM直接回答
            return await self._handle_concept_problem(problem)
    
    def _extract_expressions(self, text: str) -> list:
        """从文本中提取数学表达式"""
        import re
        
        # 寻找"表达式："后面的内容
        pattern = r'表达式：\s*([^\n]+)'
        matches = re.findall(pattern, text)
        
        expressions = []
        for match in matches:
            # 清理和验证表达式
            expr = match.strip()
            if expr and expr != "无" and expr != "-":
                expressions.append(expr)
        
        return expressions
    
    async def _handle_concept_problem(self, problem: str) -> str:
        """处理概念性问题"""
        print("📚 这是概念性问题，直接询问LLM")
        
        concept_prompt = f"""请回答这个数学概念问题：{problem}

请提供清晰、准确的解释，如果涉及公式可以展示出来。"""
        
        response = await self.llm.generate(concept_prompt)
        return response["content"]
    
    async def interactive_math_session(self):
        """交互式数学会话"""
        print(f"🎯 开始数学辅导会话 (使用 {self.provider.title()})")
        print("💡 输入数学问题，我会帮你分析和计算")
        print("💡 输入 'quit' 或 'exit' 退出")
        print("-" * 50)
        
        while True:
            try:
                problem = input("\n🧮 数学问题: ").strip()
                
                if problem.lower() in ['quit', 'exit', '退出']:
                    print("👋 数学会话结束！")
                    break
                
                if not problem:
                    continue
                
                answer = await self.solve_math_problem(problem)
                print(f"\n📖 解答:")
                print(answer)
                print("-" * 30)
                
            except KeyboardInterrupt:
                print("\n👋 会话被用户中断！")
                break
            except Exception as e:
                print(f"❌ 处理异常: {e}")


async def demo_calculator_integration():
    """演示计算器工具集成"""
    print("🚀 计算器工具集成演示")
    print("=" * 50)
    
    # 测试独立的计算器工具
    print("🔧 测试独立计算器工具:")
    calc = Calculator()
    
    test_expressions = [
        "2 + 3 * 4",
        "sqrt(16) + pow(2, 3)",
        "(15 - 3) / 4",
        "sin(pi/2) + cos(0)",
        "invalid_expression"
    ]
    
    for expr in test_expressions:
        result = calc.calculate(expr)
        status = "✅" if result["success"] else "❌"
        if result["success"]:
            print(f"  {status} {expr} = {result['result']}")
        else:
            print(f"  {status} {expr} -> {result['error']}")
    
    print(f"\n{'=' * 50}")
    print("🤖 创建数学助手:")
    
    # 创建数学助手
    providers = ["openai", "deepseek", "anthropic"]
    assistant = None
    
    for provider in providers:
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        if api_key:
            try:
                assistant = MathAssistant(provider)
                print(f"✅ 使用 {provider.title()} + 计算器工具")
                break
            except Exception as e:
                print(f"⚠️  {provider} 初始化失败: {e}")
    
    if not assistant:
        print("❌ 没有可用的API密钥")
        return assistant
    
    # 演示数学问题解决
    demo_problems = [
        "计算 25 * 4 + sqrt(36)",
        "什么是二次方程？",
        "求解 (100 - 25) / 5 + 2^3",
        "解释什么是勾股定理"
    ]
    
    print(f"\n🎯 演示数学问题解决:")
    for i, problem in enumerate(demo_problems, 1):
        print(f"\n【问题 {i}】")
        answer = await assistant.solve_math_problem(problem)
        print(f"📖 解答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        
        if i < len(demo_problems):
            await asyncio.sleep(1)
    
    return assistant


async def main():
    """主函数"""
    print("🌟 AI Modular Blocks - 计算器工具集成")
    print("展示独立工具与LLM的组合使用")
    print()
    
    assistant = await demo_calculator_integration()
    
    if assistant:
        print(f"\n🎮 是否进入交互式数学会话？(y/N)")
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                await assistant.interactive_math_session()
        except KeyboardInterrupt:
            pass
    
    print("\n🎯 核心优势:")
    print("- 独立的计算器工具，可单独使用")
    print("- LLM和工具的灵活组合")
    print("- 用户完全控制集成逻辑")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")