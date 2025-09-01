#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations

class Agent:
    """基础代理类 - 纯Python实现"""
    
    def __init__(self, name: str, role: str, provider: str = "openai"):
        self.name = name
        self.role = role
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.capabilities = []
        self.message_queue = []
        self.collaboration_history = []
    
    async def process_message(self, message: Dict, context: Dict = None) -> Dict:
        """处理来自其他代理的消息"""
        
        response_prompt = f"""
你是 {self.name}，角色：{self.role}
你的能力：{', '.join(self.capabilities)}

收到消息：
发送者：{message['from']}
类型：{message['type']}
内容：{message['content']}

上下文：{json.dumps(context or {}, ensure_ascii=False)}

请处理这个消息并提供回复。

返回JSON格式：
{{
  "response": "你的回复内容",
  "action_taken": "采取的行动",
  "next_steps": "建议的下一步",
  "confidence": 0.9
}}
"""
        
        response = await self.llm.generate(response_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content)
            
            # 记录协作历史
            self.collaboration_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "received_message",
                "from": message['from'],
                "message": message,
                "response": result
            })
            
            return result
            
        except:
            return {
                "response": f"我是{self.name}，收到了你的消息，正在处理中...",
                "action_taken": "消息接收",
                "next_steps": "等待进一步指令",
                "confidence": 0.5
            }
    
    async def send_message(self, to_agent: 'Agent', message_type: str, content: str, context: Dict = None) -> Dict:
        """向其他代理发送消息"""
        
        message = {
            "from": self.name,
            "to": to_agent.name,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # 发送消息并获取响应
        response = await to_agent.process_message(message, context)
        
        # 记录发送历史
        self.collaboration_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "sent_message",
            "to": to_agent.name,
            "message": message,
            "response": response
        })
        
        return response

class DataAnalyst(Agent):
    """数据分析师代理"""
    
    def __init__(self, provider: str = "openai"):
        super().__init__("DataAnalyst", "数据分析专家", provider)
        self.capabilities = ["数据分析", "统计计算", "趋势识别", "报告生成"]
        self.calculator = Calculator()
    
    async def analyze_data(self, data: Dict) -> Dict:
        """分析数据"""
        
        # 执行一些基本统计
        numbers = []
        if "values" in data:
            numbers = [float(x) for x in data["values"] if str(x).replace('.','').isdigit()]
        
        if numbers:
            total = sum(numbers)
            avg = total / len(numbers)
            max_val = max(numbers)
            min_val = min(numbers)
            
            analysis = {
                "count": len(numbers),
                "sum": total,
                "average": round(avg, 2),
                "max": max_val,
                "min": min_val,
                "range": max_val - min_val
            }
        else:
            analysis = {"error": "无有效数值数据"}
        
        return {
            "analyst": self.name,
            "analysis": analysis,
            "recommendations": ["需要更多数据", "建议进行深入分析"],
            "timestamp": datetime.now().isoformat()
        }

class ProjectManager(Agent):
    """项目经理代理"""
    
    def __init__(self, provider: str = "openai"):
        super().__init__("ProjectManager", "项目协调和管理", provider)
        self.capabilities = ["任务分配", "进度跟踪", "团队协调", "决策制定"]
        self.active_projects = []
    
    async def coordinate_project(self, project_goal: str, team_agents: List[Agent]) -> Dict:
        """协调项目执行"""
        
        print(f"🎯 项目经理启动项目: {project_goal}")
        
        project = {
            "id": f"proj_{datetime.now().strftime('%H%M%S')}",
            "goal": project_goal,
            "team": [agent.name for agent in team_agents],
            "status": "active",
            "start_time": datetime.now().isoformat()
        }
        
        self.active_projects.append(project)
        
        # 向团队成员分配任务
        coordination_results = []
        
        for agent in team_agents:
            task_assignment = await self.assign_task_to_agent(agent, project_goal, project)
            coordination_results.append({
                "agent": agent.name,
                "assignment": task_assignment
            })
            
            print(f"📋 已分配任务给 {agent.name}: {task_assignment['response'][:100]}...")
        
        return {
            "project": project,
            "assignments": coordination_results,
            "status": "项目已启动，任务已分配"
        }
    
    async def assign_task_to_agent(self, agent: Agent, project_goal: str, project: Dict) -> Dict:
        """分配任务给特定代理"""
        
        task_content = f"""
项目目标: {project_goal}
你的角色: {agent.role}
你的能力: {', '.join(agent.capabilities)}

请根据项目目标和你的专长，制定你负责的具体任务计划。
"""
        
        return await self.send_message(
            agent, 
            "task_assignment", 
            task_content,
            {"project": project}
        )

class TechnicalExpert(Agent):
    """技术专家代理"""
    
    def __init__(self, provider: str = "openai"):
        super().__init__("TechnicalExpert", "技术实现和架构设计", provider)
        self.capabilities = ["系统设计", "技术选型", "代码审查", "性能优化"]
        self.file_ops = FileOperations()
    
    async def design_solution(self, requirements: str) -> Dict:
        """设计技术方案"""
        
        design_prompt = f"""
需求: {requirements}

作为技术专家，请设计技术实现方案：

返回JSON:
{{
  "architecture": "架构设计描述",
  "technologies": ["技术1", "技术2"],
  "implementation_steps": ["步骤1", "步骤2"],
  "potential_challenges": ["挑战1", "挑战2"],
  "timeline_estimate": "时间估算"
}}
"""
        
        response = await self.llm.generate(design_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content)
        except:
            return {
                "architecture": "基础三层架构",
                "technologies": ["Python", "数据库"],
                "implementation_steps": ["需求分析", "设计", "开发", "测试"],
                "potential_challenges": ["性能优化", "扩展性"],
                "timeline_estimate": "4-6周"
            }

class MultiAgentSystem:
    """多代理协作系统"""
    
    def __init__(self):
        self.agents = {}
        self.message_history = []
        self.active_collaborations = []
    
    def add_agent(self, agent: Agent):
        """添加代理到系统"""
        self.agents[agent.name] = agent
        print(f"➕ 已添加代理: {agent.name} ({agent.role})")
    
    async def start_collaboration(self, project_goal: str, involved_agents: List[str]) -> Dict:
        """启动多代理协作"""
        
        print(f"🤝 启动多代理协作项目: {project_goal}")
        
        # 获取相关代理
        agents = [self.agents[name] for name in involved_agents if name in self.agents]
        
        if not agents:
            return {"error": "没有找到有效的代理"}
        
        # 如果有项目经理，让它来协调
        if "ProjectManager" in self.agents:
            pm = self.agents["ProjectManager"]
            collaboration_result = await pm.coordinate_project(project_goal, agents)
        else:
            # 没有项目经理，简单的点对点协作
            collaboration_result = await self._simple_collaboration(project_goal, agents)
        
        self.active_collaborations.append({
            "goal": project_goal,
            "agents": involved_agents,
            "start_time": datetime.now().isoformat(),
            "result": collaboration_result
        })
        
        return collaboration_result
    
    async def _simple_collaboration(self, goal: str, agents: List[Agent]) -> Dict:
        """简单的代理间协作"""
        
        results = []
        
        # 每个代理处理目标
        for agent in agents:
            individual_result = await agent.process_message({
                "from": "System",
                "type": "collaboration_request",
                "content": f"请为项目目标提供你的专业意见: {goal}"
            })
            
            results.append({
                "agent": agent.name,
                "contribution": individual_result
            })
        
        return {
            "type": "simple_collaboration",
            "goal": goal,
            "contributions": results
        }
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        
        agent_status = {}
        for name, agent in self.agents.items():
            agent_status[name] = {
                "role": agent.role,
                "capabilities": agent.capabilities,
                "message_count": len(agent.collaboration_history)
            }
        
        return {
            "total_agents": len(self.agents),
            "active_collaborations": len(self.active_collaborations),
            "agents": agent_status,
            "system_uptime": "运行中"
        }

async def main():
    """演示多代理协作系统"""
    
    print("=== 多代理协作系统演示 ===")
    
    # 创建多代理系统
    system = MultiAgentSystem()
    
    # 添加不同类型的代理
    system.add_agent(ProjectManager("openai"))
    system.add_agent(DataAnalyst("openai"))
    system.add_agent(TechnicalExpert("openai"))
    
    print(f"\n📊 系统状态:")
    status = system.get_system_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60 + "\n")
    
    # 示例1: 数据分析项目协作
    print("--- 项目1: 销售数据分析系统 ---")
    
    result1 = await system.start_collaboration(
        "开发一个销售数据分析系统，能够处理大量数据并生成可视化报告",
        ["ProjectManager", "DataAnalyst", "TechnicalExpert"]
    )
    
    print(f"🎯 协作结果:")
    if "assignments" in result1:
        for assignment in result1["assignments"]:
            print(f"  {assignment['agent']}: {assignment['assignment']['action_taken']}")
    
    print("\n" + "="*60 + "\n")
    
    # 示例2: 技术方案设计
    print("--- 项目2: AI客服系统设计 ---") 
    
    # 技术专家独立工作
    tech_expert = system.agents["TechnicalExpert"]
    design_result = await tech_expert.design_solution(
        "设计一个智能客服系统，支持多轮对话、知识库查询和人工转接"
    )
    
    print(f"🔧 技术方案:")
    print(f"架构: {design_result['architecture']}")
    print(f"技术栈: {', '.join(design_result['technologies'])}")
    print(f"预估时间: {design_result['timeline_estimate']}")
    
    # 数据分析师提供数据视角
    data_analyst = system.agents["DataAnalyst"]
    data_response = await data_analyst.process_message({
        "from": "TechnicalExpert",
        "type": "consultation",
        "content": f"技术方案: {json.dumps(design_result, ensure_ascii=False)}, 请从数据分析角度提供建议"
    })
    
    print(f"\n📊 数据分析师建议: {data_response['response']}")
    
    print(f"\n🤖 最终系统状态:")
    final_status = system.get_system_status()
    print(f"总代理数: {final_status['total_agents']}")
    print(f"协作项目数: {final_status['active_collaborations']}")

if __name__ == "__main__":
    asyncio.run(main())