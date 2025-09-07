# AI Modular Blocks - 最小化AI开发框架

## 设计哲学

**像React一样，框架语法极少，主要依赖语言特性**

- 🎯 **最小核心**：框架只提供必要的互操作性接口
- 🧩 **纯Python**：没有特殊DSL，就是标准的类、函数、异步
- ⚡ **用户自由**：不强制继承，不强制抽象，完全由用户决定实现方式
- 🔧 **模块化工具**：每个工具独立，做一件事并做好

## 三个层次的使用方式

### 1. 最小核心 (必需)

```python
# 只要这一个函数，其余全是用户自由发挥
from ai_modular_blocks import create_llm

llm = create_llm("openai", api_key="sk-...")
response = await llm.generate("Hello")
print(response["content"])
```

### 2. 独立工具 (可选)

```python
# 每个工具都独立，按需选择
from ai_modular_blocks.tools import Calculator, FileOperations, WebClient

calc = Calculator()
files = FileOperations() 
web = WebClient()

# 直接使用，无需框架包装
result = calc.calculate("2+2*3")
content = files.read_file("data.txt")
response = await web.get("https://api.example.com")
```

### 3. 用户自由实现 (推荐)

```python
# 用户完全按照自己的方式实现Agent
class MyAgent:  # 不需要继承任何框架类！
    def __init__(self):
        self.llm = create_llm("openai", api_key="sk-...")
        self.calc = Calculator()  # 选择需要的工具
    
    async def chat(self, message: str) -> str:
        # 用户自己的逻辑，想怎么写就怎么写
        if "计算" in message:
            # 使用工具
            result = self.calc.calculate("2+2")
            return f"结果是: {result['result']}"
        
        # 直接调用LLM
        response = await self.llm.generate(message)
        return response["content"]

# 纯Python，无框架束缚
agent = MyAgent()
answer = await agent.chat("帮我计算2+2")
```

## 核心原则

### ✅ 我们提供

- **LLM Provider接口**：标准化不同LLM的调用方式
- **独立工具模块**：计算器、文件操作、网络请求等
- **可选的便利函数**：快速创建和配置
- **示例和最佳实践**：展示不同的实现方式

### ❌ 我们不强制

- **继承特定基类**：用户可以完全自定义类结构
- **使用特定抽象**：Agent、Workflow等都是可选参考
- **固定的消息格式**：用户决定数据结构
- **特定的架构模式**：MVC、组件化等由用户选择

## 示例对比

### React风格 (推荐)
```python
# 就像React的函数组件
def ChatAgent(llm, tools):
    async def chat(message):
        # 纯函数逻辑
        if needs_calculation(message):
            return await handle_calc(message, tools.calc)
        return await llm.generate(message)
    return chat

# 使用
my_chat = ChatAgent(llm, tools)
response = await my_chat("Hello")
```

### 传统框架风格 (我们不推荐)
```python
# 重量级抽象，用户被框架绑定
class Agent(BaseAgent):  # 强制继承
    def process_message(self, msg: FrameworkMessage) -> FrameworkResponse:
        # 必须使用框架定义的类型和方法
        return self.framework_method(msg.framework_property)
```

## 目录结构（与当前仓库同步）

```
ai_modular_blocks/
├── core/                   # 核心接口、类型、基础实现
├── providers/              # 各种提供者实现（OpenAI/Anthropic/DeepSeek）
├── tools/                  # 独立工具 - 按需使用
│   ├── calculator.py       # 数学计算
│   ├── file_ops.py        # 文件操作  
│   └── web_client.py      # HTTP请求
└── __init__.py             # 导出 create_llm 与常用类型

examples/
├── 001_basic_llm_call/     # 快速开始
├── 002 ... 016             # 渐进式示例（多Provider/工具/代理）
└── 020_complete_application # 完整应用示例
```

## 开始使用

```bash
pip install ai-modular-blocks
```

```python
import asyncio
from ai_modular_blocks import create_llm

async def main():
    llm = create_llm("openai", api_key="your-key")
    response = await llm.generate("Hello, AI!")
    print(response["content"])

asyncio.run(main())
```

## 学习路径

1. **从最小开始**：`examples/001_basic_llm_call/`
2. **了解工具**：`examples/002-005/` - 基础功能
3. **组合使用**：`examples/006-010/` - 工具集成  
4. **自由发挥**：`examples/011-016/` + `020` - 高级应用

每个示例都展示不同的用户实现方式，没有标准答案，只有参考实现。

---

**核心理念：给你搭积木的砖块，不给你盖好的房子。怎么搭，完全由你决定。**
