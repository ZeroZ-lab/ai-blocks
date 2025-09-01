#!/usr/bin/env python3

import asyncio
import json
import os
import sys
sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations, WebClient

class SimpleReactAgent:
    """
    简单的ReACT代理 (Reason + Act)
    
    用纯Python实现的思考-行动循环，没有复杂的框架约束
    用户完全控制代理的行为逻辑
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        
        # 可用工具 - 完全用户自定义
        self.tools = {
            "calculate": Calculator(),
            "file": FileOperations(),
            "web": WebClient()
        }
    
    async def think(self, task: str, context: str = "") -> dict:
        """思考阶段 - 分析任务并决定下一步行动"""
        
        think_prompt = f"""
你是一个智能助手，需要完成以下任务: {task}

当前上下文: {context}

可用工具:
- calculate: 数学计算 (传入表达式字符串)
- file: 文件操作 (read_file/write_file/list_files)  
- web: 网页获取 (fetch URL内容)

请分析这个任务，并决定下一步应该:
1. 使用哪个工具
2. 传入什么参数
3. 为什么要这样做

返回格式:
{{
  "reasoning": "你的分析推理过程",
  "action": "工具名称",
  "action_input": "工具参数",
  "confidence": 0.95
}}

如果任务已经完成，返回:
{{
  "reasoning": "任务完成的原因",
  "action": "finished", 
  "final_answer": "最终答案"
}}
"""
        
        response = await self.llm.generate(think_prompt)
        
        try:
            # 尝试解析JSON响应
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            decision = json.loads(content)
            return decision
        except:
            # 如果解析失败，返回一个安全的默认响应
            return {
                "reasoning": f"无法解析LLM响应: {response['content'][:200]}",
                "action": "finished",
                "final_answer": "解析错误，无法继续执行"
            }
    
    async def act(self, action: str, action_input: str) -> dict:
        """行动阶段 - 执行具体的工具调用"""
        
        if action == "calculate":
            calc_result = self.tools["calculate"].calculate(action_input)
            return {
                "tool": "calculator",
                "input": action_input,
                "output": calc_result,
                "success": calc_result["success"]
            }
        
        elif action == "file":
            # 解析文件操作参数
            try:
                file_params = json.loads(action_input)
                operation = file_params.get("operation")
                
                if operation == "read":
                    result = await self.tools["file"].read_file(file_params["path"])
                elif operation == "write":
                    result = await self.tools["file"].write_file(file_params["path"], file_params["content"])
                elif operation == "list":
                    result = await self.tools["file"].list_files(file_params["path"])
                else:
                    result = {"success": False, "error": "未知的文件操作"}
                
                return {
                    "tool": "file_operations",
                    "input": file_params,
                    "output": result,
                    "success": result["success"]
                }
            except:
                return {
                    "tool": "file_operations", 
                    "input": action_input,
                    "output": {"success": False, "error": "参数解析失败"},
                    "success": False
                }
        
        elif action == "web":
            web_result = await self.tools["web"].fetch(action_input)
            return {
                "tool": "web_client",
                "input": action_input,
                "output": web_result,
                "success": web_result["success"]
            }
        
        else:
            return {
                "tool": "unknown",
                "input": action_input,
                "output": {"error": f"未知工具: {action}"},
                "success": False
            }
    
    async def solve(self, task: str, max_iterations: int = 5) -> dict:
        """解决问题的主循环 - ReACT模式"""
        
        print(f"🤖 开始解决任务: {task}")
        
        context = ""
        history = []
        
        for iteration in range(max_iterations):
            print(f"\n--- 第 {iteration + 1} 轮 ---")
            
            # 思考阶段
            print("🤔 思考中...")
            decision = await self.think(task, context)
            print(f"💭 推理: {decision.get('reasoning', '无推理过程')}")
            
            history.append({
                "iteration": iteration + 1,
                "thought": decision
            })
            
            # 检查是否完成
            if decision.get("action") == "finished":
                print(f"✅ 任务完成: {decision.get('final_answer', '无最终答案')}")
                return {
                    "task": task,
                    "status": "completed",
                    "iterations": iteration + 1,
                    "final_answer": decision.get("final_answer"),
                    "history": history
                }
            
            # 行动阶段
            action = decision.get("action")
            action_input = decision.get("action_input", "")
            
            print(f"🎯 行动: {action} <- {action_input}")
            
            action_result = await self.act(action, action_input)
            print(f"📋 结果: {action_result['success']} - {action_result.get('output', {})}")
            
            history[-1]["action"] = action_result
            
            # 更新上下文
            context += f"\n第{iteration+1}轮: 使用{action}工具, 输入{action_input}, "
            if action_result["success"]:
                context += f"成功获得结果: {action_result['output']}"
            else:
                context += f"失败: {action_result['output']}"
        
        # 达到最大迭代次数
        print(f"⏰ 达到最大迭代次数 ({max_iterations})")
        return {
            "task": task,
            "status": "max_iterations_reached",
            "iterations": max_iterations,
            "final_answer": "未在限定轮次内完成任务",
            "history": history
        }

class TaskAgent:
    """任务导向的代理 - 专注于完成具体任务"""
    
    def __init__(self, provider: str = "openai"):
        self.react_agent = SimpleReactAgent(provider)
    
    async def analyze_data_file(self, file_path: str) -> dict:
        """分析数据文件的专门任务"""
        task = f"分析文件 {file_path} 的内容，如果是数值数据则计算基本统计信息，如果是文本则提供内容摘要"
        return await self.react_agent.solve(task)
    
    async def research_topic(self, topic: str, save_results: bool = True) -> dict:
        """研究主题并保存结果的专门任务"""
        task = f"研究主题 '{topic}'，获取相关信息"
        if save_results:
            task += f"，并将结果保存到 research_{topic.replace(' ', '_')}.txt 文件中"
        return await self.react_agent.solve(task)
    
    async def solve_math_problem(self, problem: str) -> dict:
        """解决数学问题的专门任务"""
        task = f"解决数学问题: {problem}，提供详细的计算步骤"
        return await self.react_agent.solve(task)

async def main():
    """演示简单ReACT代理的使用"""
    
    # 示例1: 基础ReACT代理
    print("=== 示例1: 基础ReACT代理解决数学问题 ===")
    
    agent = SimpleReactAgent("openai")
    
    math_result = await agent.solve(
        "计算 (25 + 17) * 3 的结果，并验证这个结果是否大于100"
    )
    
    print(f"\n🎯 任务结果:")
    print(f"状态: {math_result['status']}")
    print(f"迭代次数: {math_result['iterations']}")
    print(f"最终答案: {math_result['final_answer']}")
    
    print("\n📚 执行历史:")
    for step in math_result['history']:
        print(f"  轮次 {step['iteration']}: {step['thought'].get('reasoning', 'N/A')[:100]}...")
    
    print("\n" + "="*60 + "\n")
    
    # 示例2: 任务导向代理
    print("=== 示例2: 任务导向代理 ===")
    
    task_agent = TaskAgent("openai")
    
    # 先创建一个示例数据文件
    file_ops = FileOperations()
    sample_data = "1, 2, 3, 4, 5\n6, 7, 8, 9, 10\n11, 12, 13, 14, 15"
    await file_ops.write_file("sample_data.txt", sample_data)
    
    # 让代理分析文件
    analysis_result = await task_agent.analyze_data_file("sample_data.txt")
    
    print(f"📊 数据分析结果:")
    print(f"状态: {analysis_result['status']}")  
    print(f"最终分析: {analysis_result['final_answer']}")
    
    print("\n" + "="*60 + "\n")
    
    # 示例3: 复杂推理任务
    print("=== 示例3: 复杂推理任务 ===")
    
    complex_result = await agent.solve(
        "如果一个书店今天卖了25本书，昨天卖了18本，前天卖了30本，请计算这三天的平均销量，并判断今天的销量是否高于平均水平",
        max_iterations=6
    )
    
    print(f"🧠 复杂推理结果:")
    print(f"状态: {complex_result['status']}")
    print(f"迭代: {complex_result['iterations']}")
    print(f"结论: {complex_result['final_answer']}")

if __name__ == "__main__":
    asyncio.run(main())