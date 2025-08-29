#!/usr/bin/env python3
"""
最简单的DeepSeek流式聊天示例

展示重构后的AI Modular Blocks架构如何优雅地工作：
- 使用重构后的base.llm模块  
- 展示DeepSeek provider的流式响应
- 体现"Do One Thing and Do It Well"的设计

运行前请确保：
1. pip install openai  # DeepSeek使用OpenAI兼容格式
2. 设置环境变量 DEEPSEEK_API_KEY
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 使用重构后的清晰导入（直接从模块导入避免yaml依赖）
from ai_modular_blocks.core.types.config import LLMConfig
from ai_modular_blocks.core.types.basic import ChatMessage
from ai_modular_blocks.providers.llm.deepseek_provider import DeepSeekProvider

load_dotenv()

async def main():
    """
    最简单的DeepSeek流式聊天示例
    """
    print("🚀 DeepSeek 流式聊天示例")
    print("=" * 50)
    
    # 1. 配置DeepSeek（最简配置）
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    config = LLMConfig(
        api_key=api_key,
        timeout=30.0,
        max_retries=3
    )
    
    # 2. 创建DeepSeek provider（展示重构后的架构）
    try:
        llm = DeepSeekProvider(config)
        print("✅ DeepSeek provider创建成功")
        
        # 展示provider信息
        info = llm.get_provider_info()
        print(f"📋 Provider信息:")
        print(f"   - 模型支持: {info['supported_models']}")
        print(f"   - 流式支持: {info['supports_streaming']}")
        print(f"   - API格式: {info['api_format']}")
        
    except Exception as e:
        print(f"❌ DeepSeek provider创建失败: {e}")
        if "openai" in str(e).lower():
            print("\n💡 安装依赖: pip install openai")
        return
    
    # 3. 创建聊天消息（让AI介绍自己）
    messages = [
        ChatMessage(
            role="user", 
            content="请用中文简单介绍一下你自己，包括你的能力和特点。"
        )
    ]
    
    print(f"\n🤖 向DeepSeek发送消息: {messages[0].content}")
    print("\n📡 DeepSeek流式回复:")
    print("-" * 50)
    
    # 4. 流式聊天（展示真正的能力）
    try:
        full_response = ""
        
        async for chunk in llm.stream_chat_completion(
            messages=messages,
            model="deepseek-chat",  # 使用deepseek-chat模型
            temperature=0.7
        ):
            # 打印流式内容
            content = chunk.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        
        print(f"\n{'-' * 50}")
        print(f"✅ 流式响应完成，总长度: {len(full_response)} 字符")
        
    except Exception as e:
        print(f"❌ 流式聊天失败: {e}")
        
        # 提供具体的错误处理建议
        if "authentication" in str(e).lower():
            print("\n💡 解决方案: 请检查API key是否正确")
        elif "openai" in str(e).lower():
            print("\n💡 解决方案: pip install openai")
        elif "network" in str(e).lower():
            print("\n💡 解决方案: 检查网络连接")
        else:
            print(f"\n💡 错误详情: {type(e).__name__}")


if __name__ == "__main__":
    print("🌟 AI Modular Blocks - DeepSeek流式聊天示例")
    
    # 检查是否有openai依赖
    try:
        import openai
        has_openai = True
    except ImportError:
        has_openai = False
    
    if not has_openai:
        print("⚠️  缺少openai依赖包")
        print("💡 安装命令: pip install openai")
        print()
    else:
        # 运行真实示例
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
        except Exception as e:
            print(f"\n❌ 程序异常: {e}")
    
    print("\n🎉 示例完成！")
    print("📚 更多示例请查看 examples/ 目录")
