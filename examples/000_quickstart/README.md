# AI Modular Blocks 快速上手指南

## 设计理念

AI Modular Blocks 像 React 一样，**框架语法极少，主要依赖 Python 语言特性**：

- **纯 Python**：使用标准的类、函数、异步等Python特性
- **组合优于继承**：通过组合小组件构建复杂系统  
- **最小化框架语法**：没有特殊的DSL，就是普通的Python代码
- **组件化**：每个功能都是独立的、可复用的组件

## 一分钟上手

### 1. 基础聊天 (纯Python代码，无特殊语法)

```python
import ai_modular_blocks as ai

# 标准的Python类实例化，传入参数
llm = ai.LLMProviderFactory.create_provider("openai", 
    ai.LLMConfig(api_key="sk-...", model="gpt-3.5-turbo"))

# 标准的Python异步函数调用
response = await llm.generate("你好，世界！")
print(response.content)
```

### 2. 组合多个组件 (纯Python组合模式)

```python
# 创建两个独立的组件
llm = ai.LLMProviderFactory.create_provider("openai", config)
tools = ai.BasicToolProvider()

# 纯Python类继承，没有特殊语法
class CalculatorAgent(ai.Agent):
    def __init__(self, llm, tools):
        super().__init__("calculator", "数学助手")
        # 标准的Python属性赋值
        self.llm = llm
        self.tools = tools
    
    # 标准的Python异步方法
    async def process_message(self, message: str):
        # 普通的if/else逻辑，没有特殊语法
        if "计算" in message:
            # 使用组合的工具组件
            calc_call = ai.ToolCall(id="1", name="calculate", 
                                  arguments={"expression": "2+2*3"})
            result = await self.tools.execute_tool(calc_call)
            return f"计算结果: {result.result}"
        
        # 使用组合的LLM组件
        response = await self.llm.generate(message)
        return response.content

# 标准的Python实例化和调用
agent = CalculatorAgent(llm, tools)
result = await agent.process_message("计算 2+2*3")
```

### 3. 多代理协作 (Vue 风格的声明式)

```python
import ai_modular_blocks as ai

# 声明式创建多代理系统
coordinator = ai.create_multiagent_system(max_agents=5)

# 注册代理
researcher = ai.create_agent("researcher", llm, role="研究员")
writer = ai.create_agent("writer", llm, role="文案")
reviewer = ai.create_agent("reviewer", llm, role="审核员")

await coordinator.register_agent(researcher)
await coordinator.register_agent(writer) 
await coordinator.register_agent(reviewer)

# 一行代码协调任务
result = await coordinator.coordinate_task(
    "写一篇关于AI发展的1000字文章",
    ["researcher", "writer", "reviewer"]
)
```

### 4. 智能工作流 (React 风格的组合模式)

```python
import ai_modular_blocks as ai

# 定义工作流步骤
workflow = ai.AgentWorkflow(
    id="content_creation",
    name="内容创作流程",
    steps=[
        ai.WorkflowStep(
            id="research",
            name="研究阶段", 
            agent_name="researcher",
            action="process",
            inputs={"task": "研究主题"}
        ),
        ai.WorkflowStep(
            id="write",
            name="写作阶段",
            agent_name="writer", 
            action="process",
            inputs={"task": "基于研究结果写文章"}
        ),
        ai.WorkflowStep(
            id="review",
            name="审核阶段",
            agent_name="reviewer",
            action="validate", 
            inputs={"task": "审核文章质量"}
        )
    ]
)

# 执行工作流
engine = ai.create_workflow_engine()
engine.register_workflow(workflow)

execution_id = await engine.execute_workflow(
    "content_creation", 
    {"topic": "人工智能的未来"}
)

# 监控进度
async for update in engine.stream_execution_updates(execution_id):
    print(f"进度: {update['progress']}% - {update['current_step']}")
```

## 核心优势

### 🎯 简单易用 (Vue 风格)
- **一行创建**: `llm = ai.create_llm("openai")`
- **语法糖**: 隐藏复杂的配置和初始化
- **直观API**: 函数名和参数一目了然

### 🧩 灵活组合 (React 风格)  
- **组件化**: 每个功能都是独立的组件
- **可组合**: 小组件可以组合成复杂系统
- **可扩展**: 轻松添加自定义组件

### 🚀 渐进式使用
- **入门**: 单个LLM调用
- **进阶**: 工具集成和代理
- **专家**: 多代理系统和工作流

### 📦 开箱即用
- **预设配置**: 常用场景的默认配置
- **丰富工具**: 内置计算、文件、网络等工具
- **完整示例**: 20个从简单到复杂的示例

## 下一步

查看 `examples/` 目录下的20个示例，从基础到高级，循序渐进地掌握框架的所有功能。

每个示例都可以独立运行，也可以组合使用构建更复杂的AI应用。