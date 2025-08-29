# 🚀 AI Modular Blocks - 示例代码

这里包含了使用AI Modular Blocks框架的各种示例，从最基础的LLM调用到复杂的RAG系统。

## 📁 目录结构

```
examples/
├── 01_basic_usage/          # 基础使用示例
│   ├── simple_chat.py       # 最简单的LLM对话
│   ├── provider_comparison.py  # 多Provider比较
│   └── config_example.py    # 配置示例
├── 02_rag_system/           # RAG系统示例
│   └── simple_rag.py        # 基础RAG实现
└── 03_advanced/             # 高级示例 (待开发)
```

## 🛠️ 准备工作

### 1. 安装依赖

```bash
# 基础框架
pip install ai-modular-blocks

# LLM providers (按需安装)
pip install ai-modular-blocks[openai]      # OpenAI支持
pip install ai-modular-blocks[anthropic]   # Anthropic支持

# Vector stores (按需安装)  
pip install ai-modular-blocks[chroma]      # ChromaDB支持
pip install ai-modular-blocks[pinecone]    # Pinecone支持
```

### 2. 设置API Keys

```bash
# OpenAI (必需)
export OPENAI_API_KEY="sk-your-openai-api-key"

# Anthropic (可选)  
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 📖 示例说明

### 🟢 01_basic_usage - 基础使用

最适合新手的示例，展示框架的核心功能：

- **`simple_chat.py`** - 最基础的LLM对话示例
  ```bash
  python examples/01_basic_usage/simple_chat.py
  ```

- **`provider_comparison.py`** - 同时使用多个LLM provider并比较响应
  ```bash
  python examples/01_basic_usage/provider_comparison.py
  ```

### 🟡 02_rag_system - RAG系统

展示如何构建检索增强生成(RAG)系统：

- **`simple_rag.py`** - 完整的RAG系统实现
  ```bash
  python examples/02_rag_system/simple_rag.py
  ```
  
  这个示例展示：
  - 文档向量化存储
  - 语义检索
  - 上下文生成回答

### 🔴 03_advanced - 高级示例 (开发中)

计划包含：
- 流式响应处理
- 多模态输入处理  
- 自定义中间件
- 性能监控和错误处理

## 💡 Linus式使用建议

### 数据结构第一
> "Bad programmers worry about the code. Good programmers worry about data structures."

在写AI应用前，先想清楚：
1. 你的数据是什么格式？
2. 它们之间的关系如何？
3. 数据流向哪里？

### 保持简单
> "如果实现需要超过3层缩进，重新设计它"

- 一个函数只做一件事
- 避免复杂的条件判断
- 优先使用组合而不是继承

### 先让代码跑起来
> "先让它工作，再让它优雅，最后让它快速"

1. 从最简单的示例开始（simple_chat.py）
2. 理解核心概念后再看复杂示例
3. 不要一开始就追求完美

## 🐛 遇到问题？

### 常见错误

1. **API Key未设置**
   ```
   错误: 请设置OPENAI_API_KEY环境变量
   ```
   解决：`export OPENAI_API_KEY="your-key"`

2. **依赖未安装**
   ```
   ImportError: No module named 'openai'
   ```
   解决：`pip install ai-modular-blocks[openai]`

3. **ChromaDB权限问题**
   ```
   Permission denied: ./chroma_db
   ```
   解决：确保当前目录有写权限

### 获取帮助

- 查看项目文档：`docs/`
- 提交Issue：GitHub Issues
- 阅读源码：`ai_modular_blocks/core/`

---

**记住Linus的话："Talk is cheap. Show me the code."**

直接运行示例，比看一千遍文档更有用！
