"""
004 - 带历史记录的对话示例

展示如何管理对话历史：
- 用户自定义的历史管理策略
- 纯Python列表和字典，无框架抽象
- 灵活的上下文窗口管理
- 仅使用 deepseek
"""

import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import sys

from ai_modular_blocks import create_llm, Message

load_dotenv()


class ConversationManager:
    """用户自定义的对话管理器 - 只使用 deepseek"""
    
    def __init__(self, max_history: int = 10):
        self.provider = "deepseek"
        self.llm = create_llm(
            self.provider,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.7
        )
        
        # 用户自定义的历史记录格式
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history = max_history
        
        # 添加系统消息
        self.add_system_message(
            "你是一个有用的AI助手。你会记住我们的对话历史，"
            "并根据上下文提供相关的回复。"
        )
    
    def add_system_message(self, content: str):
        """添加系统消息"""
        self.conversation_history.append({
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": "system"
        })
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.conversation_history.append({
            "role": "user", 
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": "user"
        })
    
    def add_assistant_message(self, content: str, metadata: Dict[str, Any] = None):
        """添加助手消息"""
        message = {
            "role": "assistant",
            "content": content, 
            "timestamp": datetime.now().isoformat(),
            "type": "assistant",
            "provider": self.provider
        }
        
        if metadata:
            message["metadata"] = metadata
            
        self.conversation_history.append(message)
    
    def get_recent_messages(self, count: int = None) -> List[Message]:
        """获取最近的消息，转换为框架格式"""
        count = count or self.max_history
        recent = self.conversation_history[-count:]
        
        return [
            Message(role=msg["role"], content=msg["content"])
            for msg in recent
        ]
    
    def manage_context_window(self):
        """管理上下文窗口 - 用户自定义的策略"""
        if len(self.conversation_history) > self.max_history:
            # 保留系统消息
            system_messages = [msg for msg in self.conversation_history if msg["type"] == "system"]
            other_messages = [msg for msg in self.conversation_history if msg["type"] != "system"]
            
            # 保留最近的对话
            recent_messages = other_messages[-(self.max_history - len(system_messages)):]
            
            self.conversation_history = system_messages + recent_messages
            
            print(f"🔄 上下文窗口管理: 保留了 {len(self.conversation_history)} 条消息")
    
    async def chat(self, user_input: str) -> str:
        """进行对话"""
        # 添加用户消息
        self.add_user_message(user_input)
        
        # 管理上下文窗口
        self.manage_context_window()
        
        # 准备消息列表
        messages = self.get_recent_messages()
        
        try:
            # 调用LLM
            response = await self.llm.generate_from_messages(messages)
            answer = response["content"]
            
            # 添加助手回复
            metadata = {
                "usage": response.usage,
                "model": response.model
            }
            self.add_assistant_message(answer, metadata)
            
            return answer
            
        except Exception as e:
            error_msg = f"抱歉，我遇到了一些问题：{str(e)}"
            self.add_assistant_message(error_msg)
            return error_msg
    
    def show_conversation_summary(self):
        """显示对话摘要"""
        print("\n📊 对话摘要:")
        print(f"  总消息数: {len(self.conversation_history)}")
        
        by_type = {}
        for msg in self.conversation_history:
            msg_type = msg["type"]
            by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        for msg_type, count in by_type.items():
            print(f"  {msg_type}: {count} 条")
    
    def export_conversation(self, filename: str):
        """导出对话历史"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, 
                         ensure_ascii=False, indent=2)
            print(f"✅ 对话历史已导出到: {filename}")
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def load_conversation(self, filename: str):
        """加载对话历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            print(f"✅ 对话历史已从 {filename} 加载")
        except Exception as e:
            print(f"❌ 加载失败: {e}")


async def demo_conversation_with_context():
    """演示带上下文的对话（只用 deepseek）"""
    print("🚀 带历史记录的对话演示")
    print("=" * 50)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 没有可用的DEEPSEEK_API_KEY")
        return
    
    try:
        manager = ConversationManager(max_history=8)
        print(f"✅ 使用 Deepseek 提供商")
    except Exception as e:
        print(f"❌ Deepseek 初始化失败: {e}")
        return
    
    # 模拟一个有上下文的对话
    conversation_flow = [
        "我叫Alice，我是一名软件工程师",
        "我最喜欢的编程语言是Python",
        "你还记得我的名字吗？",
        "我刚才说我喜欢什么编程语言？",
        "能推荐一些Python的高级特性给我学习吗？",
        "谢谢！你觉得装饰器在实际项目中有什么用途？"
    ]
    
    print("\n🎭 模拟对话流程:")
    for i, user_message in enumerate(conversation_flow, 1):
        print(f"\n【轮次 {i}】")
        print(f"👤 Alice: {user_message}")
        
        response = await manager.chat(user_message)
        print(f"🤖 助手: {response}")
        
        # 显示当前历史记录数量
        print(f"💭 当前历史: {len(manager.conversation_history)} 条消息")
        
        await asyncio.sleep(1)  # 模拟真实对话间隔
    
    # 显示最终摘要
    manager.show_conversation_summary()
    
    # 导出对话
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    manager.export_conversation(filename)
    
    return manager


async def interactive_mode():
    """交互模式（只用 deepseek）"""
    print("\n🎮 进入交互模式")
    print("💡 输入 'history' 查看对话摘要")
    print("💡 输入 'export' 导出对话历史") 
    print("💡 输入 'quit' 退出")
    print("-" * 40)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 没有可用的DEEPSEEK_API_KEY")
        return
    
    try:
        manager = ConversationManager()
        print(f"✅ 使用 Deepseek 开始对话")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'history':
                manager.show_conversation_summary()
                continue
            elif user_input.lower() == 'export':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                manager.export_conversation(f"chat_{timestamp}.json")
                continue
            elif not user_input:
                continue
            
            response = await manager.chat(user_input)
            print(f"🤖 助手: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 对话异常: {e}")
    
    print("\n👋 对话结束！")


async def main():
    """主函数"""
    print("🌟 AI Modular Blocks - 带历史记录的对话")
    print("展示用户自定义的对话历史管理（只用 deepseek）")
    print()
    
    # 演示模式
    manager = await demo_conversation_with_context()
    
    if manager and sys.stdin.isatty():
        print(f"\n🎮 是否进入交互模式？(y/N)")
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                await interactive_mode()
        except KeyboardInterrupt:
            pass
    
    print("\n🎯 核心特点:")
    print("- 用户完全控制历史记录的格式和存储")
    print("- 灵活的上下文窗口管理策略")
    print("- 支持对话导出和加载功能")
    print("- 仅使用 deepseek 作为 LLM 提供商")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
