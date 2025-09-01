"""
AI Modular Blocks 快速上手示例

展示框架的简洁易用性，类似 Vue 的语法糖和 React 的组合能力
"""

import asyncio
import os
from typing import List, Optional

# 导入框架 - 简洁的导入方式
import ai_modular_blocks as ai


async def example_1_basic_llm():
    """
    示例1: 基础LLM调用 (Vue风格的语法糖)
    一行代码创建，直接使用
    """
    print("=== 示例1: 基础LLM调用 ===")
    
    # 语法糖: 一行创建LLM
    llm = ai.create_llm(
        "openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    
    # 简单调用
    response = await llm.generate("用一句话介绍人工智能")
    print(f"AI回复: {response.content}")
    print()


async def example_2_with_tools():
    """
    示例2: 带工具的对话 (React风格的组合)
    组合LLM和工具提供者
    """
    print("=== 示例2: 工具集成 ===")
    
    # 组合基础组件
    llm = ai.create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
    tools = ai.BasicToolProvider()
    
    # 简单的工具使用
    available_tools = await tools.get_available_tools()
    print(f"可用工具数量: {len(available_tools)}")
    
    # 模拟工具调用
    calc_call = ai.ToolCall(
        id="calc_1",
        name="calculate",
        arguments={"expression": "2+2*3"}
    )
    
    result = await tools.execute_tool(calc_call)
    print(f"计算结果: {result.result}")
    print()


class SimpleAgent(ai.ConversationalAgent):
    """
    示例3: 自定义代理类 (继承和组合)
    结合Vue的简洁性和React的组合能力
    """
    
    def __init__(self, name: str, llm: ai.LLMProvider, tools: Optional[ai.ToolProvider] = None):
        super().__init__(name, f"{name} - 智能助手")
        self.llm = llm
        self.tools = tools
    
    async def process_message(self, message: str, **kwargs) -> ai.AgentResponse:
        """处理消息的核心逻辑"""
        
        # 记录对话历史
        await self.update_conversation_history("user", message)
        
        # 生成回复
        response = await self.llm.generate(message)
        
        # 记录AI回复
        await self.update_conversation_history("assistant", response.content)
        
        return ai.AgentResponse(
            content=response.content,
            actions=[],
            state=self.state,
            is_complete=True
        )
    
    async def generate_response(self, message: str) -> str:
        """简化的响应生成"""
        response = await self.process_message(message)
        return response.content
    
    async def update_conversation_history(self, role: str, content: str) -> None:
        """更新对话历史"""
        message = ai.Message(role=role, content=content)
        self.state.conversation_history.append(message)
        # 保持历史记录在合理长度
        if len(self.state.conversation_history) > 20:
            self.state.conversation_history = self.state.conversation_history[-20:]


async def example_3_custom_agent():
    """
    示例3: 自定义代理
    """
    print("=== 示例3: 自定义代理 ===")
    
    llm = ai.create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
    agent = SimpleAgent("助手", llm)
    
    # 连续对话
    questions = [
        "你好！", 
        "你能做什么？",
        "帮我解释什么是机器学习"
    ]
    
    for question in questions:
        response = await agent.generate_response(question)
        print(f"用户: {question}")
        print(f"助手: {response}")
        print()


async def example_4_multiagent_simple():
    """
    示例4: 简单的多代理协作
    声明式的多代理系统
    """
    print("=== 示例4: 多代理协作 ===")
    
    # 创建多代理协调器
    coordinator = ai.create_multiagent_system(max_agents=3)
    
    # 创建不同角色的代理
    llm = ai.create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
    
    analyst = SimpleAgent("分析师", llm)
    writer = SimpleAgent("作家", llm) 
    editor = SimpleAgent("编辑", llm)
    
    # 注册代理
    await coordinator.register_agent(analyst)
    await coordinator.register_agent(writer)
    await coordinator.register_agent(editor)
    
    print("多代理系统状态:")
    status = coordinator.get_agent_status()
    print(f"- 总代理数: {status['total_agents']}")
    print(f"- 空闲代理: {len(status['idle_agents'])}")
    
    # 简单的任务协调
    try:
        result = await coordinator.coordinate_task(
            "分析当前AI发展趋势并写一段总结",
            ["分析师", "作家", "编辑"]
        )
        
        print(f"协作结果: {result['success']}")
        if result['success']:
            print("各代理执行情况:")
            for agent_name, agent_result in result['results'].items():
                print(f"- {agent_name}: {'成功' if agent_result['success'] else '失败'}")
    except Exception as e:
        print(f"协作执行出错: {e}")
    
    print()


async def example_5_workflow_simple():
    """
    示例5: 简单工作流
    """
    print("=== 示例5: 简单工作流 ===")
    
    # 创建工作流引擎
    engine = ai.create_workflow_engine()
    
    # 注册一个代理到工作流引擎
    llm = ai.create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))
    agent = SimpleAgent("工作流助手", llm)
    engine.register_agent(agent)
    
    # 定义简单的工作流
    workflow = ai.AgentWorkflow(
        id="simple_task",
        name="简单任务流程",
        description="演示基础工作流功能",
        steps=[
            ai.WorkflowStep(
                id="step1",
                name="分析任务",
                agent_name="工作流助手",
                action="process",
                inputs={"task": "分析输入的问题"}
            ),
            ai.WorkflowStep(
                id="step2", 
                name="生成方案",
                agent_name="工作流助手",
                action="process",
                inputs={"task": "基于分析结果生成解决方案"}
            )
        ]
    )
    
    # 注册工作流
    engine.register_workflow(workflow)
    
    try:
        # 执行工作流
        execution_id = await engine.execute_workflow(
            "simple_task",
            {"input": "如何提高团队工作效率？"}
        )
        
        print(f"工作流执行ID: {execution_id}")
        
        # 等待执行完成
        await asyncio.sleep(2)
        
        # 检查执行状态
        status = await engine.get_execution_status(execution_id)
        if status:
            print(f"执行状态: {status['status']}")
            print(f"进度: {status['progress']:.1f}%")
            
    except Exception as e:
        print(f"工作流执行出错: {e}")
    
    print()


async def main():
    """
    主函数 - 演示所有示例
    """
    print("AI Modular Blocks - 快速上手示例")
    print("=" * 50)
    
    examples = [
        example_1_basic_llm,
        example_2_with_tools, 
        example_3_custom_agent,
        example_4_multiagent_simple,
        example_5_workflow_simple
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            await example_func()
        except Exception as e:
            print(f"示例{i}执行出错: {e}")
            print("(提示: 请确保设置了正确的API密钥)")
            print()
    
    print("所有示例执行完成!")
    print("\n接下来可以查看 examples/ 目录下的更多详细示例。")


if __name__ == "__main__":
    asyncio.run(main())