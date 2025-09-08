# 🧱 AI Modular Blocks

> 模块化AI开发框架 - 像搭乐高一样构建AI应用

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#)

## 🚀 30秒快速开始

```bash
# 安装
pip install ai-modular-blocks[openai,chroma]

# 设置API Key
export OPENAI_API_KEY="your-key"
```

```python
# 运行第一个AI应用
python examples/001_basic_llm_call/main.py
```

## 📖 完整文档

详细的架构设计、API参考和开发指南：

**👉 [查看完整文档](docs/README.md)**

- 规划与优化清单：`docs/TODO.md`

## 🎯 核心特性

- 🔌 **模块化设计** - 可组合、可替换的AI组件
- ⚡ **高性能** - 连接池、缓存、并发优化
- 🛡️ **生产就绪** - 完整的错误处理、监控、测试
- 🎨 **开发友好** - 类型安全、智能提示、详细文档

## 📁 项目结构

```
ai-modular-blocks/
├── examples/               # 🎯 从这里开始
│   ├── 001_basic_llm_call/ # 基础LLM使用
│   ├── 002 ... 016         # 提供商对比、流式、工具与代理
│   └── 020_complete_application/ # 完整应用
├── ai_modular_blocks/      # 📦 核心代码
└── docs/                  # 📖 详细文档
```

## 🤝 参与贡献

我们欢迎所有形式的贡献！请查看 [完整文档](docs/README.md#🔧-开发指南) 了解详细的贡献指南。

---

**💡 设计理念**: "好的AI应用是通过组合最佳的专业化工具构建的，而不是依赖单一框架。"
