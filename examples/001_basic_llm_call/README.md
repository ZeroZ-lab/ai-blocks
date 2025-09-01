# 001 - 基础LLM调用

最简单的AI Modular Blocks示例，展示框架的核心设计哲学。

## 🎯 设计哲学

AI Modular Blocks遵循**React哲学** - 提供最小化的API，依赖Python语言特性：

- **极简API**: 只需要 `create_llm()` 一个函数
- **纯Python**: 没有特殊语法，完全使用Python语言特性
- **用户自主**: 完全控制应用逻辑和数据流

## 🚀 快速开始

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key-here"

# 运行示例
python main.py
```

## 📝 代码核心

```python
# 这就是全部的框架API！
from ai_modular_blocks import create_llm

# 创建LLM实例
llm = create_llm("openai", api_key=os.getenv("OPENAI_API_KEY"))

# 生成回复
response = await llm.generate("你好")
print(response["content"])
```

## 🌟 关键特点

1. **极简**: 只需要一个函数调用
2. **直观**: 标准的Python异步代码
3. **灵活**: 用户完全控制交互逻辑
4. **无依赖**: 不需要额外的配置文件

## 💡 学习要点

这个示例展示了框架的核心理念：

- **给你构建块，不给你约束**
- **依赖Python语言特性，不是框架魔法**
- **让你专注创造价值，而不是学习框架**

## 📚 下一步

学会了基础调用后，可以尝试：

- [002 多提供商比较](../002_multi_provider_comparison/) - 切换不同的LLM提供商
- [006 工具集成](../006_basic_tools/) - 为LLM添加计算器等工具
- [020 完整应用](../020_complete_application/) - 看看框架的完整能力