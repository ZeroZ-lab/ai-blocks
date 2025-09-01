#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations

class TaskPlan:
    """任务计划 - 纯Python数据结构"""
    
    def __init__(self, name: str, description: str, priority: int = 1):
        self.name = name
        self.description = description
        self.priority = priority  # 1-5, 5最重要
        self.status = "pending"  # pending, in_progress, completed, failed
        self.subtasks = []
        self.dependencies = []
        self.estimated_time = None
        self.actual_time = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.metadata = {}
    
    def add_subtask(self, subtask: 'TaskPlan'):
        """添加子任务"""
        self.subtasks.append(subtask)
    
    def add_dependency(self, dependency: str):
        """添加依赖任务"""
        self.dependencies.append(dependency)
    
    def start(self):
        """开始执行任务"""
        self.status = "in_progress"
        self.started_at = datetime.now()
    
    def complete(self, result: Any = None):
        """完成任务"""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.result = result
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.actual_time = duration.total_seconds()
    
    def fail(self, error: str):
        """任务失败"""
        self.status = "failed"
        self.result = {"error": error}
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "dependencies": self.dependencies,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "metadata": self.metadata
        }

class PlanningAgent:
    """
    规划代理 - 能够制定和执行复杂计划
    
    用纯Python实现任务规划、依赖管理、执行调度
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        
        # 计划管理
        self.active_plans = {}  # plan_id -> TaskPlan
        self.execution_history = []
        
        # 代理能力
        self.capabilities = [
            "数学计算", "文件操作", "数据分析", "报告生成", "任务规划"
        ]
    
    async def create_plan(self, goal: str, context: Dict = None) -> TaskPlan:
        """为目标创建详细计划"""
        
        print(f"🎯 开始为目标制定计划: {goal}")
        
        context_str = ""
        if context:
            context_str = f"\n上下文信息: {json.dumps(context, ensure_ascii=False)}"
        
        planning_prompt = f"""
你是一个专业的任务规划师。请为以下目标制定详细的执行计划:

目标: {goal}
{context_str}

我的能力范围: {', '.join(self.capabilities)}

请分析这个目标，并创建一个结构化的计划，包含:
1. 主要任务分解
2. 子任务的优先级 (1-5, 5最重要)
3. 任务之间的依赖关系
4. 预估完成时间 (分钟)
5. 所需工具

返回JSON格式:
{{
  "main_task": "主任务名称",
  "description": "详细描述",
  "priority": 5,
  "estimated_time": 30,
  "subtasks": [
    {{
      "name": "子任务1",
      "description": "详细描述",
      "priority": 3,
      "estimated_time": 10,
      "dependencies": [],
      "tools_needed": ["calculator"]
    }},
    {{
      "name": "子任务2", 
      "description": "详细描述",
      "priority": 4,
      "estimated_time": 15,
      "dependencies": ["子任务1"],
      "tools_needed": ["file_ops"]
    }}
  ]
}}
"""
        
        response = await self.llm.generate(planning_prompt)
        
        try:
            # 解析计划JSON
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            plan_data = json.loads(content)
            
            # 创建主计划
            main_plan = TaskPlan(
                name=plan_data["main_task"],
                description=plan_data["description"],
                priority=plan_data["priority"]
            )
            main_plan.estimated_time = plan_data.get("estimated_time", 0) * 60  # 转换为秒
            
            # 创建子任务
            subtask_map = {}  # name -> TaskPlan
            
            for subtask_data in plan_data.get("subtasks", []):
                subtask = TaskPlan(
                    name=subtask_data["name"],
                    description=subtask_data["description"],
                    priority=subtask_data["priority"]
                )
                subtask.estimated_time = subtask_data.get("estimated_time", 0) * 60
                subtask.metadata["tools_needed"] = subtask_data.get("tools_needed", [])
                
                main_plan.add_subtask(subtask)
                subtask_map[subtask.name] = subtask
            
            # 设置依赖关系
            for subtask_data in plan_data.get("subtasks", []):
                subtask = subtask_map[subtask_data["name"]]
                for dep in subtask_data.get("dependencies", []):
                    subtask.add_dependency(dep)
            
            # 保存计划
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.active_plans[plan_id] = main_plan
            main_plan.metadata["plan_id"] = plan_id
            
            print(f"📋 计划创建完成 (ID: {plan_id})")
            print(f"   主任务: {main_plan.name}")
            print(f"   子任务数: {len(main_plan.subtasks)}")
            print(f"   预估时间: {main_plan.estimated_time/60:.1f} 分钟")
            
            return main_plan
            
        except Exception as e:
            print(f"❌ 计划解析失败: {e}")
            # 创建一个简单的后备计划
            fallback_plan = TaskPlan(
                name=f"简单计划: {goal}",
                description=f"为目标 '{goal}' 创建的基础计划",
                priority=3
            )
            return fallback_plan
    
    async def execute_plan(self, plan: TaskPlan) -> Dict:
        """执行计划"""
        
        print(f"🚀 开始执行计划: {plan.name}")
        plan.start()
        
        execution_log = []
        successful_tasks = 0
        failed_tasks = 0
        
        try:
            # 按依赖关系排序子任务
            sorted_subtasks = self._sort_by_dependencies(plan.subtasks)
            
            for subtask in sorted_subtasks:
                print(f"\n📌 执行子任务: {subtask.name}")
                subtask.start()
                
                # 执行子任务
                task_result = await self._execute_single_task(subtask)
                
                if task_result["success"]:
                    subtask.complete(task_result["result"])
                    successful_tasks += 1
                    print(f"   ✅ 完成: {task_result.get('message', 'OK')}")
                else:
                    subtask.fail(task_result["error"])
                    failed_tasks += 1
                    print(f"   ❌ 失败: {task_result['error']}")
                
                execution_log.append({
                    "task": subtask.name,
                    "success": task_result["success"],
                    "result": task_result,
                    "duration": subtask.actual_time
                })
            
            # 完成主计划
            plan_success = failed_tasks == 0
            if plan_success:
                plan.complete({
                    "successful_tasks": successful_tasks,
                    "failed_tasks": failed_tasks,
                    "execution_log": execution_log
                })
                print(f"\n🎉 计划执行成功!")
            else:
                plan.fail(f"有 {failed_tasks} 个子任务失败")
                print(f"\n⚠️  计划部分失败: {failed_tasks} 个任务失败")
            
            return {
                "plan_id": plan.metadata.get("plan_id"),
                "success": plan_success,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "total_time": plan.actual_time,
                "execution_log": execution_log
            }
            
        except Exception as e:
            plan.fail(f"执行异常: {str(e)}")
            print(f"💥 计划执行异常: {e}")
            return {
                "plan_id": plan.metadata.get("plan_id"),
                "success": False,
                "error": str(e),
                "execution_log": execution_log
            }
    
    def _sort_by_dependencies(self, tasks: List[TaskPlan]) -> List[TaskPlan]:
        """根据依赖关系排序任务"""
        sorted_tasks = []
        remaining = tasks.copy()
        completed_names = set()
        
        while remaining:
            # 找到没有未满足依赖的任务
            ready_tasks = []
            for task in remaining:
                deps_satisfied = all(dep in completed_names for dep in task.dependencies)
                if deps_satisfied:
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # 如果没有可执行的任务，可能存在循环依赖，按优先级排序
                ready_tasks = sorted(remaining, key=lambda t: t.priority, reverse=True)[:1]
            
            # 添加到执行队列
            for task in ready_tasks:
                sorted_tasks.append(task)
                completed_names.add(task.name)
                remaining.remove(task)
        
        return sorted_tasks
    
    async def _execute_single_task(self, task: TaskPlan) -> Dict:
        """执行单个任务"""
        
        tools_needed = task.metadata.get("tools_needed", [])
        
        # 根据任务描述判断需要执行的操作
        execution_prompt = f"""
任务: {task.name}
描述: {task.description}
需要的工具: {tools_needed}

请分析这个任务需要执行什么具体操作。如果需要:
- 数学计算: 返回计算表达式
- 文件操作: 返回文件操作指令
- 数据分析: 返回分析步骤
- 其他: 返回具体行动

返回JSON格式:
{{
  "action_type": "calculate|file|analysis|other",
  "action_details": "具体的操作内容",
  "expected_result": "预期结果描述"
}}
"""
        
        try:
            response = await self.llm.generate(execution_prompt)
            content = response["content"].strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            action = json.loads(content)
            action_type = action.get("action_type", "other")
            action_details = action.get("action_details", "")
            
            # 根据动作类型执行
            if action_type == "calculate" and "calculator" in tools_needed:
                calc_result = self.calculator.calculate(action_details)
                if calc_result["success"]:
                    return {
                        "success": True,
                        "result": calc_result["result"],
                        "message": f"计算 {action_details} = {calc_result['result']}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"计算失败: {calc_result['error']}"
                    }
            
            elif action_type == "file" and "file_ops" in tools_needed:
                # 简单的文件操作示例
                if "读取" in action_details or "read" in action_details.lower():
                    # 模拟文件读取
                    return {
                        "success": True,
                        "result": "文件内容示例",
                        "message": "文件读取成功"
                    }
                elif "写入" in action_details or "write" in action_details.lower():
                    # 模拟文件写入
                    return {
                        "success": True,
                        "result": "文件已写入",
                        "message": "文件写入成功"
                    }
            
            # 默认处理 - 模拟任务完成
            return {
                "success": True,
                "result": f"已完成: {action_details}",
                "message": f"任务 '{task.name}' 执行完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"任务执行失败: {str(e)}"
            }
    
    async def save_plan_to_file(self, plan: TaskPlan, filename: str = None):
        """保存计划到文件"""
        if not filename:
            plan_id = plan.metadata.get("plan_id", "unknown")
            filename = f"{plan_id}_plan.json"
        
        plan_data = {
            "plan": plan.to_dict(),
            "saved_at": datetime.now().isoformat()
        }
        
        await self.file_ops.write_file(filename, json.dumps(plan_data, ensure_ascii=False, indent=2))
        print(f"💾 计划已保存到: {filename}")
    
    def get_plan_status(self, plan: TaskPlan) -> Dict:
        """获取计划状态摘要"""
        subtasks_by_status = {}
        for subtask in plan.subtasks:
            status = subtask.status
            if status not in subtasks_by_status:
                subtasks_by_status[status] = 0
            subtasks_by_status[status] += 1
        
        return {
            "plan_name": plan.name,
            "status": plan.status,
            "total_subtasks": len(plan.subtasks),
            "subtasks_by_status": subtasks_by_status,
            "estimated_time": f"{plan.estimated_time/60:.1f} 分钟" if plan.estimated_time else "未估计",
            "actual_time": f"{plan.actual_time/60:.1f} 分钟" if plan.actual_time else "未完成",
            "created_at": plan.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

async def main():
    """演示规划代理的使用"""
    
    print("=== 智能规划代理演示 ===")
    
    agent = PlanningAgent("openai")
    
    # 示例1: 创建简单计划
    print("\n--- 示例1: 数据分析项目计划 ---")
    
    plan1 = await agent.create_plan(
        "分析公司过去3个月的销售数据，计算关键指标并生成报告",
        context={
            "数据来源": "sales_data.csv",
            "关键指标": ["总销售额", "平均客单价", "增长率"],
            "报告格式": "PDF"
        }
    )
    
    # 显示计划详情
    status = agent.get_plan_status(plan1)
    print(f"📊 计划状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    # 执行计划
    result1 = await agent.execute_plan(plan1)
    print(f"\n🎯 执行结果:")
    print(f"  成功: {result1['success']}")
    print(f"  成功任务: {result1['successful_tasks']}")
    print(f"  失败任务: {result1['failed_tasks']}")
    
    print("\n" + "="*60 + "\n")
    
    # 示例2: 复杂多步骤计划
    print("--- 示例2: 投资分析计划 ---")
    
    plan2 = await agent.create_plan(
        "为客户制定投资组合，包括风险评估、收益计算和推荐方案",
        context={
            "客户资金": "100万",
            "风险偏好": "中等",
            "投资期限": "5年",
            "投资类型": ["股票", "债券", "基金"]
        }
    )
    
    # 保存计划
    await agent.save_plan_to_file(plan2)
    
    # 执行计划
    result2 = await agent.execute_plan(plan2)
    
    print(f"\n💼 投资计划执行结果:")
    print(f"  计划ID: {result2['plan_id']}")
    print(f"  总耗时: {result2.get('total_time', 0)/60:.1f} 分钟")
    print(f"  执行日志: {len(result2['execution_log'])} 步骤")
    
    # 显示最终计划状态
    final_status = agent.get_plan_status(plan2)
    print(f"\n📈 最终状态:")
    for key, value in final_status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())