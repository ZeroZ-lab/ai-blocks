#!/usr/bin/env python3
"""
001 - 基础LLM调用

展示AI Modular Blocks的核心设计哲学：
• 极简API：只需要 create_llm() 一个函数
• 纯Python：没有特殊语法，完全依赖Python语言特性  
• 用户自主：完全控制交互逻辑
"""

import asyncio
import os
import sys

# 添加父目录到path以导入框架
sys.path.append('../..')

from ai_modular_blocks import create_llm
from dotenv import load_dotenv

load_dotenv()


async def main():
    """最基础的LLM调用示例"""
    
    print("🚀 AI Modular Blocks - 基础示例")
    print("展示最简单的LLM调用")
    print("="*50)
    
    # 这就是框架的全部API！
    # 创建DeepSeek Chat LLM实例只需要一行代码
    llm = create_llm(
        "deepseek",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat"
    )
    
    print("✅ LLM创建成功")
    
    # 基础对话示例
    print("\n💬 基础对话:")
    response = await llm.generate("你好，请简单介绍一下自己")
    print(f"🤖 回复: {response['content']}")
    
    # 中文交互示例  
    print("\n🇨🇳 中文交互:")
    response = await llm.generate("什么是人工智能？请用一段话解释")
    print(f"🤖 回复: {response['content']}")
    
    # 编程任务示例
    print("\n💻 编程任务:")
    response = await llm.generate("用Python写一个计算斐波那契数列的函数")
    print(f"🤖 回复: {response['content']}")
    
    print("\n" + "="*50)
    print("✅ 基础示例完成!")
    print("\n🎯 关键要点:")
    print("  • 只需要 create_llm() 一个函数")
    print("  • 没有复杂的配置和设置")  
    print("  • 完全是标准的Python异步代码")
    print("  • 用户完全控制对话逻辑")

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
        print("示例: export DEEPSEEK_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("🌟 AI Modular Blocks 框架核心理念:")
    print("给你最小但强大的构建块，让你用纯Python创造任何AI应用！")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print("💡 请检查API密钥是否正确设置")