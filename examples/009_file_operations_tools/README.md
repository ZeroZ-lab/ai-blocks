# 009 - 文件操作工具

展示如何将LLM与文件操作工具结合，创建强大的代码分析和处理系统。

## 特点

- **代码分析**: 自动分析代码库结构和质量
- **智能重构**: 根据需求重构代码文件  
- **文档生成**: 自动生成项目文档
- **纯Python组合**: 完全用标准Python语法组合工具

## 功能

1. **CodeAnalysisAssistant**: 代码库分析和重构
2. **DocumentationGenerator**: 自动文档生成

## 使用方法

```bash
# 设置环境变量
export OPENAI_API_KEY="your-key-here"

# 运行示例
python main.py
```

## 核心组件

### CodeAnalysisAssistant
- 扫描Python文件
- LLM分析代码质量
- 智能代码重构
- 自动备份原文件

### DocumentationGenerator  
- 分析项目结构
- 自动生成README.md
- 基于代码内容生成文档

## 关键概念

- **工具独立性**: FileOperations可以单独使用
- **用户自主组合**: 完全由用户决定如何组合LLM和文件工具
- **安全操作**: 自动备份，避免数据丢失

## 扩展想法

- 添加更多文件格式支持
- 实现代码审查功能
- 添加测试用例生成
- 支持多语言代码分析