"""
002 - 多提供商模型对比示例

展示如何用相同的代码调用不同的LLM提供商：
- 统一的接口，无需学习不同的API
- 用户可以轻松切换和对比不同模型
- 纯Python实现，无框架特殊语法
"""

import asyncio
import os
from dotenv import load_dotenv

from ai_modular_blocks import create_llm

load_dotenv()


class ModelComparator:
    """用户自定义的模型对比器 - 无需继承任何框架类！"""
    
    def __init__(self):
        # 配置不同的提供商
        self.models = {}
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.models["OpenAI GPT-3.5"] = create_llm(
                "openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4o-mini",
                temperature=0.7,
                base_url="https://api.ephone.ai/v1"
            )
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.models["Anthropic Claude"] = create_llm(
                "openai", 
                api_key=os.getenv("OPENAI_API_KEY"),
                model="claude-3-5-haiku-latest",
                temperature=0.7,
                base_url="https://api.ephone.ai/v1"
            )
        
        # DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            self.models["DeepSeek Chat"] = create_llm(
                "deepseek",
                api_key=os.getenv("DEEPSEEK_API_KEY"), 
                model="deepseek-chat",
                temperature=0.7,
                base_url="https://api.deepseek.com"
            )
    
    async def compare_responses(self, question: str):
        """对比不同模型对同一问题的回答"""
        print(f"🤔 问题: {question}")
        print("=" * 60)
        
        results = {}
        
        for model_name, llm in self.models.items():
            print(f"\n🤖 {model_name}:")
            print("-" * 40)
            
            try:
                response = await llm.generate(question)
                answer = response["content"]
                
                # 记录结果
                results[model_name] = {
                    "answer": answer,
                    "length": len(answer),
                    "usage": response.get("usage", {})
                }
                
                # 显示回答（截取前200字符）
                display_answer = answer[:200] + "..." if len(answer) > 200 else answer
                print(display_answer)
                
                # 显示使用统计
                if response.get("usage"):
                    print(f"\n📊 使用统计: {response['usage']}")
                
            except Exception as e:
                print(f"❌ 调用失败: {e}")
                results[model_name] = {"error": str(e)}
        
        return results
    
    def analyze_results(self, results: dict):
        """分析对比结果"""
        print(f"\n{'=' * 60}")
        print("📈 对比分析:")
        
        successful_results = {k: v for k, v in results.items() if "error" not in v}
        
        if not successful_results:
            print("❌ 所有模型都调用失败")
            return
        
        # 比较回答长度
        lengths = [(k, v["length"]) for k, v in successful_results.items()]
        lengths.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n📏 回答长度对比:")
        for model_name, length in lengths:
            print(f"  {model_name}: {length} 字符")
        
        # 比较token使用（如果有）
        print(f"\n🔢 Token使用对比:")
        for model_name, result in successful_results.items():
            usage = result.get("usage")
            if usage:
                total_tokens = usage.get("total_tokens", "未知")
                print(f"  {model_name}: {total_tokens} tokens")
            else:
                print(f"  {model_name}: 无使用统计")


async def main():
    """主函数"""
    print("🚀 多提供商模型对比示例")
    print("展示统一接口调用不同LLM提供商")
    print()
    
    # 创建对比器 - 用户自定义的类，无需继承
    comparator = ModelComparator()
    
    if not comparator.models:
        print("⚠️  未检测到任何有效的API密钥")
        print("请设置以下环境变量中的至少一个:")
        print("- OPENAI_API_KEY")
        print("- ANTHROPIC_API_KEY") 
        print("- DEEPSEEK_API_KEY")
        return
    
    print(f"✅ 已配置 {len(comparator.models)} 个模型:")
    for model_name in comparator.models:
        print(f"  - {model_name}")
    
    # 测试问题
    questions = [
        "什么是人工智能？请用一句话概括",
        "写一个Python函数计算斐波那契数列",
        "推荐5个学习编程的网站"
    ]
    
    # 对比不同问题
    for i, question in enumerate(questions, 1):
        print(f"\n🔍 测试 {i}/{len(questions)}")
        results = await comparator.compare_responses(question)
        comparator.analyze_results(results)
        
        if i < len(questions):
            print(f"\n{'⏸️ ' * 20}")
            await asyncio.sleep(1)  # 避免API限流


if __name__ == "__main__":
    print("🌟 AI Modular Blocks - 多提供商对比")
    print("同一套代码，调用不同的LLM提供商")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
    
    print("\n🎯 核心优势:")
    print("- 统一的API接口，无需学习不同提供商的SDK")
    print("- 轻松切换和对比不同模型")
    print("- 用户可以自由定义对比逻辑和分析方式")