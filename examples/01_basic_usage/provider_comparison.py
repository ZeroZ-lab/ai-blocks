#!/usr/bin/env python3
"""
多Provider比较示例

展示如何同时使用多个LLM提供商并比较响应。
真实场景中很有用的功能。
"""

import asyncio
import os
from ai_modular_blocks.providers.llm import LLMProviderFactory
from ai_modular_blocks.core.types import LLMConfig, ChatMessage


async def compare_providers():
    """比较不同provider的响应"""
    
    LLMProviderFactory.initialize()
    
    # 检查API keys
    providers_config = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers_config.append({
            "name": "OpenAI",
            "provider": "openai",
            "config": LLMConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=100,
                temperature=0.7
            )
        })
    
    if os.getenv("ANTHROPIC_API_KEY"):
        providers_config.append({
            "name": "Anthropic",
            "provider": "anthropic", 
            "config": LLMConfig(
                provider="anthropic",
                model="claude-3-haiku-20240307",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=100,
                temperature=0.7
            )
        })
    
    if not providers_config:
        print("❌ 没有可用的API keys，请设置OPENAI_API_KEY或ANTHROPIC_API_KEY")
        return
    
    # 准备测试消息
    test_message = [
        ChatMessage(role="user", content="用一句话解释什么是人工智能")
    ]
    
    print("🧪 同一个问题，不同Provider的回答对比:")
    print(f"❓ 问题: {test_message[0].content}")
    print("-" * 50)
    
    # 并发调用所有可用的providers
    tasks = []
    for config in providers_config:
        provider = LLMProviderFactory.create_provider(config["provider"], config["config"])
        task = asyncio.create_task(
            call_provider_with_name(provider, config["name"], test_message)
        )
        tasks.append(task)
    
    # 等待所有结果
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ 错误: {result}")


async def call_provider_with_name(provider, name, messages):
    """调用provider并格式化输出"""
    try:
        response = await provider.generate(messages)
        print(f"🤖 {name}: {response.content}")
        print(f"   Token: {response.usage}")
        print()
    except Exception as e:
        print(f"❌ {name} 错误: {e}")
        print()


if __name__ == "__main__":
    print("=== AI Modular Blocks - Provider比较示例 ===")
    asyncio.run(compare_providers())
