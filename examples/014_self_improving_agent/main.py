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

class SelfImprovingAgent:
    """
    自我改进代理 - 通过反思和学习提升性能
    
    纯Python实现，用户完全控制改进逻辑
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        
        # 性能跟踪
        self.performance_log = []
        self.learned_patterns = {}
        self.improvement_history = []
        
        # 知识库
        self.knowledge_base = {
            "successful_strategies": [],
            "common_mistakes": [],
            "optimization_tips": []
        }
    
    async def execute_task_with_reflection(self, task: str) -> Dict:
        """执行任务并进行反思改进"""
        
        print(f"🎯 执行任务: {task}")
        start_time = datetime.now()
        
        # 1. 基于历史经验优化任务执行
        optimized_approach = await self._optimize_approach(task)
        print(f"💡 优化策略: {optimized_approach['strategy']}")
        
        # 2. 执行任务
        result = await self._execute_with_monitoring(task, optimized_approach)
        
        # 3. 性能反思
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        reflection = await self._reflect_on_performance(task, result, execution_time)
        
        # 4. 学习和改进
        await self._learn_from_experience(task, result, reflection)
        
        return {
            "task": task,
            "result": result,
            "execution_time": execution_time,
            "reflection": reflection,
            "improvements_learned": len(self.improvement_history)
        }
    
    async def _optimize_approach(self, task: str) -> Dict:
        """基于历史经验优化执行方法"""
        
        # 查找相似任务的成功策略
        similar_patterns = []
        for pattern in self.learned_patterns.get("successful", []):
            if any(keyword in task.lower() for keyword in pattern.get("keywords", [])):
                similar_patterns.append(pattern)
        
        context = ""
        if similar_patterns:
            context = f"历史成功策略: {json.dumps(similar_patterns[-3:], ensure_ascii=False)}"
        
        optimization_prompt = f"""
任务: {task}
{context}

基于历史经验和最佳实践，请提供优化的执行策略:

返回JSON:
{{
  "strategy": "具体策略描述",
  "key_steps": ["步骤1", "步骤2"],
  "potential_risks": ["风险1", "风险2"],
  "success_metrics": ["指标1", "指标2"]
}}
"""
        
        response = await self.llm.generate(optimization_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content)
        except:
            return {
                "strategy": "标准执行流程",
                "key_steps": ["分析任务", "执行操作", "验证结果"],
                "potential_risks": ["执行失败"],
                "success_metrics": ["任务完成"]
            }
    
    async def _execute_with_monitoring(self, task: str, approach: Dict) -> Dict:
        """执行任务并监控性能"""
        
        try:
            # 简化的任务执行逻辑
            if "计算" in task or "数学" in task:
                # 提取并执行数学计算
                calc_prompt = f"从任务中提取数学表达式: {task}"
                calc_response = await self.llm.generate(calc_prompt)
                
                # 简单提取逻辑
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', task)
                if len(numbers) >= 2:
                    expr = f"{numbers[0]} + {numbers[1]}"  # 简化示例
                    calc_result = self.calculator.calculate(expr)
                    if calc_result["success"]:
                        return {
                            "success": True,
                            "result": calc_result["result"],
                            "method": "数学计算",
                            "details": f"计算了 {expr} = {calc_result['result']}"
                        }
            
            # 通用任务处理
            execution_prompt = f"""
执行任务: {task}
策略: {approach['strategy']}

请提供执行结果和详细过程。
"""
            
            response = await self.llm.generate(execution_prompt)
            
            return {
                "success": True,
                "result": response["content"][:500],
                "method": "LLM分析",
                "details": "通过语言模型完成任务分析"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "异常处理",
                "details": f"执行过程中发生错误: {str(e)}"
            }
    
    async def _reflect_on_performance(self, task: str, result: Dict, execution_time: float) -> Dict:
        """反思任务执行的性能"""
        
        reflection_prompt = f"""
刚才执行了任务: {task}
执行结果: {json.dumps(result, ensure_ascii=False)}
执行时间: {execution_time:.2f}秒

请反思这次执行的表现:

返回JSON:
{{
  "performance_rating": 8,
  "what_went_well": ["优点1", "优点2"],
  "what_could_improve": ["改进点1", "改进点2"],
  "key_learnings": ["学习点1", "学习点2"],
  "optimization_suggestions": ["建议1", "建议2"]
}}
"""
        
        response = await self.llm.generate(reflection_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            reflection = json.loads(content)
            
            # 记录性能
            self.performance_log.append({
                "task": task,
                "rating": reflection.get("performance_rating", 5),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return reflection
            
        except:
            return {
                "performance_rating": 5,
                "what_went_well": ["任务完成"],
                "what_could_improve": ["提高效率"],
                "key_learnings": ["积累经验"],
                "optimization_suggestions": ["优化流程"]
            }
    
    async def _learn_from_experience(self, task: str, result: Dict, reflection: Dict):
        """从经验中学习"""
        
        # 提取任务关键词
        task_keywords = task.lower().split()[:5]
        
        # 如果性能良好，记录成功模式
        if reflection.get("performance_rating", 0) >= 7:
            success_pattern = {
                "task_type": task[:50],
                "keywords": task_keywords,
                "strategy": result.get("method", "unknown"),
                "success_factors": reflection.get("what_went_well", []),
                "timestamp": datetime.now().isoformat()
            }
            
            if "successful" not in self.learned_patterns:
                self.learned_patterns["successful"] = []
            self.learned_patterns["successful"].append(success_pattern)
            
            # 限制存储数量
            if len(self.learned_patterns["successful"]) > 20:
                self.learned_patterns["successful"] = self.learned_patterns["successful"][-20:]
        
        # 记录改进建议
        improvements = reflection.get("optimization_suggestions", [])
        if improvements:
            self.improvement_history.append({
                "task": task,
                "improvements": improvements,
                "timestamp": datetime.now().isoformat()
            })
        
        # 更新知识库
        self.knowledge_base["successful_strategies"].extend(
            reflection.get("what_went_well", [])
        )
        self.knowledge_base["optimization_tips"].extend(
            reflection.get("optimization_suggestions", [])
        )
        
        # 限制知识库大小
        for category in self.knowledge_base:
            if len(self.knowledge_base[category]) > 50:
                self.knowledge_base[category] = self.knowledge_base[category][-50:]
    
    def get_improvement_summary(self) -> Dict:
        """获取自我改进的摘要"""
        
        # 计算平均性能评分
        ratings = [log["rating"] for log in self.performance_log]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # 最近的改进趋势
        recent_ratings = ratings[-10:] if len(ratings) >= 10 else ratings
        recent_avg = sum(recent_ratings) / len(recent_ratings) if recent_ratings else 0
        
        return {
            "total_tasks": len(self.performance_log),
            "average_performance": round(avg_rating, 2),
            "recent_performance": round(recent_avg, 2),
            "improvement_trend": "上升" if recent_avg > avg_rating else "稳定",
            "learned_patterns": len(self.learned_patterns.get("successful", [])),
            "knowledge_base_size": {
                category: len(items) for category, items in self.knowledge_base.items()
            },
            "top_strategies": self.knowledge_base["successful_strategies"][-5:],
            "recent_optimizations": [h["improvements"] for h in self.improvement_history[-3:]]
        }

async def main():
    """演示自我改进代理"""
    
    print("=== 自我改进代理演示 ===")
    
    agent = SelfImprovingAgent("openai")
    
    # 执行一系列任务，观察自我改进过程
    tasks = [
        "计算 100 和 200 的和",
        "分析数字序列 1, 4, 9, 16 的规律",
        "计算 50 乘以 3 的结果",
        "解释什么是复利效应",
        "计算 15 的平方根"
    ]
    
    print("开始执行任务序列，观察代理的自我改进...\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"--- 任务 {i} ---")
        
        result = await agent.execute_task_with_reflection(task)
        
        print(f"执行时间: {result['execution_time']:.2f}秒")
        print(f"性能评分: {result['reflection']['performance_rating']}/10")
        print(f"成功因素: {result['reflection']['what_went_well']}")
        print(f"改进建议: {result['reflection']['optimization_suggestions']}")
        print()
    
    # 显示学习成果
    print("="*60)
    print("🧠 自我改进总结:")
    
    summary = agent.get_improvement_summary()
    print(f"总任务数: {summary['total_tasks']}")
    print(f"平均性能: {summary['average_performance']}/10")
    print(f"最近性能: {summary['recent_performance']}/10")
    print(f"改进趋势: {summary['improvement_trend']}")
    print(f"学会的模式: {summary['learned_patterns']} 个")
    
    print(f"\n📚 知识库大小:")
    for category, size in summary['knowledge_base_size'].items():
        print(f"  {category}: {size} 项")
    
    print(f"\n🏆 顶级策略:")
    for strategy in summary['top_strategies'][-3:]:
        print(f"  • {strategy}")

if __name__ == "__main__":
    asyncio.run(main())