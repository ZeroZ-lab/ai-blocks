# Core Module

核心模块 - AI Modular Blocks的基础架构层

## 🎯 设计原则

遵循Unix哲学：**"Do One Thing and Do It Well"**

- **单一职责** - 每个模块专注一个领域
- **接口优先** - 清晰的抽象定义
- **组合优于继承** - 通过接口组装功能
- **向后兼容** - Never Break Userspace

## 📁 目录结构

```
core/
├── types/           # 类型定义 - 数据结构和类型别名
├── interfaces/      # 接口定义 - 抽象基类和协议
├── base.py         # 基础实现 - 通用Provider基类
├── config.py       # 配置管理 - 系统配置和环境管理
├── exceptions.py   # 异常体系 - 结构化错误处理
└── validators.py   # 验证器 - 输入验证和安全检查
```

## 🔧 核心组件

### 类型系统 (`types/`)
- **基础类型**: 消息、响应、文档等核心数据结构
- **工具类型**: Function Calling和工具执行相关类型
- **MCP类型**: Model Context Protocol协议类型
- **配置类型**: 各种Provider的配置结构

### 接口系统 (`interfaces/`)
- **LLM接口**: 语言模型提供商抽象
- **存储接口**: 向量存储和嵌入服务抽象
- **工具接口**: 工具注册和执行抽象
- **MCP接口**: Model Context Protocol实现抽象
- **工具类接口**: 缓存、中间件、插件等工具抽象

## 📖 使用示例

```python
# 基础类型使用
from ai_modular_blocks.core.types import ChatMessage, LLMResponse, ToolDefinition

# 接口使用
from ai_modular_blocks.core.interfaces import LLMProvider, ToolProvider

# 统一导入（推荐）
from ai_modular_blocks.core import (
    LLMProvider,
    ChatMessage, 
    ToolDefinition,
    ValidationException
)
```

## 🏗️ 扩展指南

1. **添加新类型**: 在`types/`对应模块中定义
2. **添加新接口**: 在`interfaces/`对应模块中定义
3. **保持向后兼容**: 在各自`__init__.py`中导出
4. **遵循命名约定**: 接口以`Provider`结尾，类型使用清晰的名词

## 🔍 设计哲学

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry

每个组件都经过精心设计，确保：
- **最小复杂度** - 避免过度设计
- **最大透明度** - 用户知道每一步在做什么
- **最强可控性** - 用户可以控制每个环节
