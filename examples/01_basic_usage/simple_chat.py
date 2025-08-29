#!/usr/bin/env python3
"""
最基础的LLM聊天示例

这个示例展示如何使用ai-modular-blocks进行最简单的LLM对话。
不需要复杂配置，直接可用。
"""

import asyncio
import os
from ai_modular_blocks.providers.llm import LLMProviderFactory
from ai_modular_blocks.core.types import LLMConfig, ChatMessage


async def simple_chat_example():
    """最简单的聊天示例"""
    
    # 1. 初始化工厂
    LLMProviderFactory.initialize()
    
    # 2. 创建OpenAI provider（需要设置OPENAI_API_KEY环境变量）
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请设置OPENAI_API_KEY环境变量")
        return
    
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=100,
        temperature=0.7
    )
    
    llm = LLMProviderFactory.create_provider("openai", config)
    
    # 3. 发送简单消息
    messages = [
        ChatMessage(role="user", content="你好！请简单介绍一下你自己。")
    ]
    
    print("🤖 正在思考...")
    response = await llm.generate(messages)
    
    print(f"✅ 回复: {response.content}")
    print(f"📊 Token使用: {response.usage}")


if __name__ == "__main__":
    # 运行示例
    print("=== AI Modular Blocks - 基础聊天示例 ===")
    asyncio.run(simple_chat_example())
