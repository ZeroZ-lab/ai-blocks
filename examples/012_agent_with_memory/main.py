#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations

class SimpleMemory:
    """
    简单的记忆系统 - 用纯Python实现
    
    用户完全控制记忆的存储和检索逻辑
    """
    
    def __init__(self):
        self.short_term = []  # 短期记忆 - 当前会话
        self.long_term = {}   # 长期记忆 - 持久化存储
        self.working_memory = {}  # 工作记忆 - 当前任务相关
    
    def add_short_term(self, memory_type: str, content: Any, metadata: Dict = None):
        """添加短期记忆"""
        memory_item = {
            "timestamp": datetime.now().isoformat(),
            "type": memory_type,
            "content": content,
            "metadata": metadata or {}
        }
        self.short_term.append(memory_item)
        
        # 限制短期记忆大小
        if len(self.short_term) > 50:
            self.short_term = self.short_term[-50:]
    
    def add_long_term(self, key: str, value: Any, category: str = "general"):
        """添加长期记忆"""
        if category not in self.long_term:
            self.long_term[category] = {}
        
        self.long_term[category][key] = {
            "value": value,
            "created": datetime.now().isoformat(),
            "access_count": 0
        }
    
    def get_long_term(self, key: str, category: str = "general") -> Any:
        """获取长期记忆"""
        if category in self.long_term and key in self.long_term[category]:
            item = self.long_term[category][key]
            item["access_count"] += 1
            item["last_accessed"] = datetime.now().isoformat()
            return item["value"]
        return None
    
    def search_short_term(self, query: str, memory_type: str = None) -> List[Dict]:
        """搜索短期记忆"""
        results = []
        for memory in self.short_term:
            if memory_type and memory["type"] != memory_type:
                continue
            
            content_str = str(memory["content"]).lower()
            if query.lower() in content_str:
                results.append(memory)
        
        return results[-10:]  # 返回最近的10条匹配记录
    
    def get_working_context(self) -> str:
        """获取当前工作上下文"""
        context_parts = []
        
        # 添加工作记忆
        if self.working_memory:
            context_parts.append("当前任务信息:")
            for key, value in self.working_memory.items():
                context_parts.append(f"  {key}: {value}")
        
        # 添加最近的短期记忆
        recent_memories = self.short_term[-5:]
        if recent_memories:
            context_parts.append("\n最近的行为:")
            for memory in recent_memories:
                context_parts.append(f"  {memory['type']}: {str(memory['content'])[:100]}")
        
        return "\n".join(context_parts)
    
    def save_to_file(self, file_path: str):
        """保存记忆到文件"""
        memory_data = {
            "long_term": self.long_term,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, file_path: str):
        """从文件加载记忆"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            self.long_term = memory_data.get("long_term", {})
            return True
        except FileNotFoundError:
            return False

class MemoryAgent:
    """
    带记忆的智能代理
    
    展示如何用纯Python为代理添加记忆能力
    """
    
    def __init__(self, provider: str = "openai", memory_file: str = "agent_memory.json"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.memory = SimpleMemory()
        self.memory_file = memory_file
        
        # 工具
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        
        # 加载历史记忆
        self.memory.load_from_file(memory_file)
        
        # 代理人格和设定
        self.personality = {
            "name": "Alex",
            "role": "智能助手",
            "traits": ["细心", "逻辑性强", "记忆力好"]
        }
    
    async def remember_interaction(self, user_input: str, agent_response: str, action_taken: str = None):
        """记住交互过程"""
        
        # 短期记忆 - 对话
        self.memory.add_short_term("user_input", user_input)
        self.memory.add_short_term("agent_response", agent_response)
        
        if action_taken:
            self.memory.add_short_term("action", action_taken)
        
        # 分析是否需要长期记忆
        analysis_prompt = f"""
用户说: {user_input}
我回复: {agent_response}

这次交互中是否包含需要长期记住的重要信息？比如:
- 用户的个人信息或偏好
- 重要的计算结果
- 文件路径或数据位置
- 任务的完成状态

如果有，请返回JSON格式:
{{
  "should_remember": true,
  "key": "记忆的键名",
  "value": "要记住的值",
  "category": "信息类别"
}}

如果没有重要信息，返回:
{{"should_remember": false}}
"""
        
        try:
            analysis = await self.llm.generate(analysis_prompt)
            content = analysis["content"].strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            decision = json.loads(content)
            
            if decision.get("should_remember"):
                self.memory.add_long_term(
                    decision["key"],
                    decision["value"], 
                    decision.get("category", "general")
                )
                print(f"💾 长期记忆已保存: {decision['key']}")
        
        except:
            pass  # 分析失败不影响主流程
    
    async def think_with_memory(self, user_input: str) -> str:
        """结合记忆进行思考"""
        
        # 更新工作记忆
        self.memory.working_memory["current_task"] = user_input
        self.memory.working_memory["timestamp"] = datetime.now().isoformat()
        
        # 搜索相关的历史记忆
        relevant_memories = self.memory.search_short_term(user_input)
        
        # 获取工作上下文
        context = self.memory.get_working_context()
        
        # 检查是否有相关的长期记忆
        long_term_context = ""
        for category in self.memory.long_term:
            for key, data in self.memory.long_term[category].items():
                if any(word in key.lower() or word in str(data["value"]).lower() 
                       for word in user_input.lower().split()):
                    long_term_context += f"\n记住的{category}: {key} = {data['value']}"
        
        # 构造思考提示
        think_prompt = f"""
你是{self.personality['name']}，一个{self.personality['role']}。
你的特点: {', '.join(self.personality['traits'])}

用户输入: {user_input}

当前上下文:
{context}

相关的长期记忆:
{long_term_context}

相关的历史交互:
{json.dumps(relevant_memories[-3:], ensure_ascii=False, indent=2) if relevant_memories else '无'}

基于你的记忆和上下文，请提供有帮助的回答。如果需要使用计算器，请明确说出计算表达式。
保持你的个性特点，并体现出你记住了之前的交互。
"""
        
        response = await self.llm.generate(think_prompt)
        return response["content"]
    
    async def process_request(self, user_input: str) -> dict:
        """处理用户请求的完整流程"""
        
        print(f"👤 用户: {user_input}")
        
        # 结合记忆思考
        response = await self.think_with_memory(user_input)
        print(f"🤖 {self.personality['name']}: {response}")
        
        # 检查是否需要执行工具操作
        action_taken = None
        
        # 简单的工具触发逻辑 (实际应用中可以更智能)
        if "计算" in user_input or "算" in user_input:
            # 提取计算表达式
            calc_prompt = f"""
从以下文本中提取需要计算的数学表达式: {user_input}

只返回一个可以直接计算的表达式，比如: 25*1.05**5
如果没有明确的计算需求，返回: NONE
"""
            
            calc_analysis = await self.llm.generate(calc_prompt)
            expression = calc_analysis["content"].strip()
            
            if expression != "NONE" and expression:
                calc_result = self.calculator.calculate(expression)
                if calc_result["success"]:
                    action_taken = f"计算: {expression} = {calc_result['result']}"
                    response += f"\n\n📊 计算结果: {expression} = {calc_result['result']}"
        
        # 记住这次交互
        await self.remember_interaction(user_input, response, action_taken)
        
        # 保存记忆
        self.memory.save_to_file(self.memory_file)
        
        return {
            "user_input": user_input,
            "response": response,
            "action_taken": action_taken,
            "memory_items": len(self.memory.short_term),
            "long_term_categories": len(self.memory.long_term)
        }
    
    def get_memory_summary(self) -> dict:
        """获取记忆摘要"""
        return {
            "short_term_memories": len(self.memory.short_term),
            "long_term_categories": list(self.memory.long_term.keys()),
            "working_memory": self.memory.working_memory,
            "recent_interactions": [
                f"{m['type']}: {str(m['content'])[:50]}..."
                for m in self.memory.short_term[-5:]
            ]
        }

async def main():
    """演示带记忆的代理"""
    
    print("=== 带记忆的智能代理演示 ===")
    
    agent = MemoryAgent("openai", "demo_memory.json")
    
    # 模拟一系列交互
    conversations = [
        "你好，我叫小明，今年25岁，是一名程序员",
        "请帮我计算 1000 * 1.05 的 10次方，这是我的投资收益",
        "我刚才问的投资计算结果是多少？还有你还记得我的职业吗？",
        "如果我每年再投入2000元，20年后总共会有多少钱？",
        "总结一下我们刚才讨论的投资话题"
    ]
    
    print(f"开始连续对话，展示记忆能力...\n")
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n--- 对话 {i} ---")
        
        result = await agent.process_request(user_input)
        
        if result["action_taken"]:
            print(f"🔧 执行了: {result['action_taken']}")
        
        # 在某些节点显示记忆状态
        if i in [2, 4]:
            print(f"\n📋 记忆状态:")
            summary = agent.get_memory_summary()
            print(f"  短期记忆: {summary['short_term_memories']} 条")
            print(f"  长期记忆类别: {summary['long_term_categories']}")
            print(f"  最近交互: {summary['recent_interactions'][-2:]}")
    
    print(f"\n" + "="*60)
    print(f"🧠 最终记忆摘要:")
    final_summary = agent.get_memory_summary()
    print(json.dumps(final_summary, ensure_ascii=False, indent=2))
    
    # 演示记忆持久化 - 重启代理
    print(f"\n🔄 重启代理，测试记忆持久化...")
    new_agent = MemoryAgent("openai", "demo_memory.json")
    
    restart_result = await new_agent.process_request("你还记得我是谁吗？我们之前讨论过什么？")
    print(f"重启后的记忆测试完成！")

if __name__ == "__main__":
    asyncio.run(main())