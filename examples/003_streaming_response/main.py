"""
003 - 流式响应处理示例

本示例仅测试 deepseek 的流式响应：
- 实时显示生成内容
- 用户可以自定义流式处理逻辑
- 纯Python异步迭代器模式
"""

import asyncio
import os
import time
from dotenv import load_dotenv

from ai_modular_blocks import create_llm

load_dotenv()


class StreamingChatBot:
    """仅用于 deepseek 的流式聊天机器人"""

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未找到 deepseek 的API密钥 (请设置 DEEPSEEK_API_KEY 环境变量)")

        # 创建LLM实例
        self.llm = create_llm(
            "deepseek",
            api_key=api_key,
            model="deepseek-chat",
            temperature=0.8
        )
        self.provider = "deepseek"

    async def stream_chat(self, message: str):
        """流式聊天 - 用户自定义的实现"""
        print(f"👤 用户: {message}")
        print(f"🤖 {self.provider.title()}: ", end="", flush=True)

        full_response = ""
        start_time = time.time()

        try:
            # 检查是否支持流式响应
            if hasattr(self.llm, 'stream_generate'):
                # 流式生成
                async for chunk in self.llm.stream_generate(message):
                    if chunk and hasattr(chunk, 'content') and chunk.content:
                        content = chunk.content
                        print(content, end="", flush=True)
                        full_response += content

                        # 模拟打字机效果
                        await asyncio.sleep(0.01)
            else:
                # 降级到普通生成
                response = await self.llm.generate(message)
                content = response["content"]

                # 模拟流式效果
                for char in content:
                    print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)

            end_time = time.time()
            duration = end_time - start_time

            print(f"\n\n⏱️  生成耗时: {duration:.2f}秒")
            print(f"📏 回复长度: {len(full_response)} 字符")

            return full_response

        except Exception as e:
            print(f"\n❌ 流式生成失败: {e}")
            return None

    async def interactive_chat(self):
        """交互式聊天"""
        print(f"🎯 开始与 {self.provider.title()} 进行流式对话")
        print("💡 输入 'quit' 或 'exit' 退出")
        print("-" * 50)

        while True:
            try:
                # 获取用户输入
                user_input = input("\n👤 你: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break

                if not user_input:
                    print("⚠️  请输入有效内容")
                    continue

                # 流式生成回复
                await self.stream_chat(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 对话异常: {e}")


async def demo_streaming():
    """演示 deepseek 的流式处理方式"""
    print("🚀 流式响应演示 (仅 deepseek)")
    print("=" * 50)

    # 尝试创建 deepseek 聊天机器人
    try:
        bot = StreamingChatBot()
        print(f"✅ 使用 Deepseek 提供商")
    except ValueError as e:
        print(f"❌ {e}")
        print("请设置环境变量: DEEPSEEK_API_KEY")
        return

    # 演示不同类型的问题
    demo_questions = [
        "请写一首关于程序员的诗",
        "解释什么是递归，并给出Python示例",
        "推荐一本好看的科幻小说，并说明理由"
    ]

    print(f"\n🎬 演示流式响应（共{len(demo_questions)}个问题）")

    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"📝 演示问题 {i}: {question}")
        print("-" * 60)

        response = await bot.stream_chat(question)

        if i < len(demo_questions):
            print("\n⏯️  暂停2秒后继续...")
            await asyncio.sleep(2)

    print(f"\n{'=' * 60}")
    print("🎉 演示完成！")

    # 询问是否进入交互模式
    print("\n🎮 是否进入交互聊天模式？(y/N)")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes', 'Y', '是']:
            await bot.interactive_chat()
    except KeyboardInterrupt:
        print("\n👋 再见！")


async def main():
    """主函数"""
    print("🌟 AI Modular Blocks - 流式响应示例 (仅 deepseek)")
    print("展示实时生成和自定义流式处理")
    print()

    await demo_streaming()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")

    print("\n🎯 学习要点:")
    print("- 流式响应提供更好的用户体验")
    print("- 用户可以自定义流式处理逻辑")
    print("- 支持降级到普通模式的兼容性处理")