# AI Modular Blocks 示例集合

完整的AI应用示例，从简单到复杂，展示框架的强大功能和设计哲学。

## 🎯 设计哲学

AI Modular Blocks 遵循 **React 哲学** - 提供最小化的API，依赖Python语言特性而非框架语法糖：

- **极简API**: 只需 `create_llm()` 即可开始
- **纯Python**: 没有特殊DSL，完全使用Python语言特性  
- **用户自主**: 完全控制应用逻辑和数据流
- **Do One Thing Well**: 每个工具都专注单一功能

## 📚 示例目录

### 🟢 基础示例 (001-005)
| 示例 | 描述 | 核心概念 |
|------|------|----------|
| [001_basic_llm_call](001_basic_llm_call/) | 最基本的LLM调用 | 框架入门，极简API |
| [002_multi_provider_comparison](002_multi_provider_comparison/) | 多提供商比较 | 统一接口，提供商切换 |
| [003_streaming_responses](003_streaming_responses/) | 流式响应处理 | 实时交互，用户体验 |
| [004_custom_prompting](004_custom_prompting/) | 自定义提示工程 | 提示优化，输出控制 |
| [005_error_handling](005_error_handling/) | 错误处理和重试 | 健壮性，错误恢复 |

### 🔧 工具集成 (006-010)
| 示例 | 描述 | 核心概念 |
|------|------|----------|
| [006_basic_tools](006_basic_tools/) | 基础工具使用 | 工具独立性，简单集成 |
| [007_calculator_tools](007_calculator_tools/) | 数学计算工具 | 精确计算，结果验证 |
| [008_web_search_tools](008_web_search_tools/) | 网页搜索工具 | 信息获取，内容分析 |
| [009_file_operations_tools](009_file_operations_tools/) | 文件操作工具 | 数据持久化，文件处理 |
| [010_multi_tool_orchestration](010_multi_tool_orchestration/) | 多工具协调 | 工作流编排，复杂任务 |

### 🤖 智能代理 (011-015)
| 示例 | 描述 | 核心概念 |
|------|------|----------|
| [011_simple_react_agent](011_simple_react_agent/) | 简单ReACT代理 | 思考-行动循环，推理透明 |
| [012_agent_with_memory](012_agent_with_memory/) | 带记忆的代理 | 上下文保持，学习能力 |
| [013_planning_agent](013_planning_agent/) | 规划代理 | 目标分解，任务调度 |
| [014_self_improving_agent](014_self_improving_agent/) | 自我改进代理 | 性能反思，持续优化 |
| [015_multi_modal_agent](015_multi_modal_agent/) | 多模态代理 | 输入识别，专门处理 |

### 🚀 高级应用 (016-020)
| 示例 | 描述 | 核心概念 |
|------|------|----------|
| [016_multi_agent_collaboration](016_multi_agent_collaboration/) | 多代理协作 | 角色分工，消息通信 |
| [017_workflow_orchestration](017_workflow_orchestration/) | 工作流编排 | 流程自动化，状态管理 |
| [018_distributed_computing](018_distributed_computing/) | 分布式计算 | 并行处理，资源调度 |
| [019_ai_powered_system](019_ai_powered_system/) | AI驱动系统 | 智能决策，系统集成 |
| [020_complete_application](020_complete_application/) | **完整应用** | 企业级功能，端到端流程 |

## 🎓 学习路径

### 🌟 初学者路径
1. **001** - 理解框架基础
2. **006** - 学习工具集成  
3. **011** - 尝试智能代理
4. **020** - 体验完整应用

### 💼 开发者路径  
1. **002** - 多提供商支持
2. **005** - 错误处理机制
3. **010** - 复杂工具协调
4. **013** - 智能任务规划

### 🏗️ 架构师路径
1. **015** - 多模态处理
2. **016** - 多代理协作
3. **017** - 工作流编排
4. **018** - 分布式系统

## 🚀 快速开始

```bash
# 1. 设置环境变量
export OPENAI_API_KEY="your-key-here"

# 2. 运行最简单的示例
cd 001_basic_llm_call
python main.py

# 3. 尝试完整应用
cd ../020_complete_application  
python main.py
```

## 🔑 核心特点

### ✨ React-like 简洁性
```python
# 这就是全部 API！
from ai_modular_blocks import create_llm

llm = create_llm("openai", api_key="sk-...")
response = await llm.generate("你好")
print(response["content"])
```

### 🧩 独立工具组合
```python
# 工具完全独立，可以单独使用
from ai_modular_blocks.tools import Calculator, FileOperations

calc = Calculator()
file_ops = FileOperations()

# 用户完全控制如何组合
result = calc.calculate("100 * 1.05**5")
await file_ops.write_file("result.txt", str(result))
```

### 🎨 纯Python实现
```python
# 没有特殊语法，全部是标准Python
class MyAgent:
    def __init__(self):
        self.llm = create_llm("openai", api_key="...")
        self.tools = {"calc": Calculator()}
    
    async def solve(self, problem):
        # 用户自己的逻辑
        return await self.llm.generate(problem)
```

## 💡 最佳实践

1. **从简单开始**: 先运行 001 基础示例
2. **理解哲学**: 框架只提供构建块，不强制特定模式  
3. **工具独立**: 每个工具都可以单独测试和使用
4. **纯Python**: 使用标准面向对象和异步模式
5. **用户自主**: 你完全控制应用的行为逻辑

## 🌟 核心价值

AI Modular Blocks 让你专注于**创造价值**而非学习框架：

- **学习成本低**: 会Python就会用
- **集成成本低**: 工具独立，渐进集成
- **维护成本低**: 代码清晰，架构简单  
- **扩展成本低**: 添加新功能很容易

## 🤝 参与贡献

这些示例展示了框架的可能性，欢迎你：

- 运行示例并提供反馈
- 创建新的应用场景
- 贡献独立工具
- 分享使用心得

---

**记住框架的核心理念：给你最小但强大的构建块，让你用纯Python创造任何AI应用！**