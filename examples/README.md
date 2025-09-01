# AI应用示例集合

本目录包含20个从简单到复杂的AI应用示例，展示ai-modular-blocks框架的全面使用场景。

## 示例分类和复杂度

### 🟢 基础示例 (1-5)
- **001_basic_llm_call** - 基础模型调用
- **002_multi_provider_comparison** - 多提供商模型对比
- **003_streaming_response** - 流式响应处理
- **004_chat_with_history** - 带历史记录的对话
- **005_prompt_templates** - 提示模板使用

### 🟡 工具集成示例 (6-10)
- **006_basic_function_calling** - 基础函数调用
- **007_calculator_tools** - 计算器工具集成
- **008_weather_api_integration** - 天气API集成
- **009_file_operations_tools** - 文件操作工具
- **010_web_search_integration** - 网络搜索集成

### 🟠 智能代理示例 (11-15)
- **011_basic_react_agent** - 基础ReACT智能代理
- **012_task_planning_agent** - 任务规划代理
- **013_code_analysis_agent** - 代码分析代理
- **014_research_assistant_agent** - 研究助手代理
- **015_customer_service_agent** - 客服代理

### 🔴 高级应用示例 (16-20)
- **016_multi_agent_conversation** - 多代理对话系统
- **017_rag_knowledge_base** - RAG知识库应用
- **018_document_processing_pipeline** - 文档处理流水线
- **019_realtime_monitoring_system** - 实时监控系统
- **020_intelligent_workflow_orchestrator** - 智能工作流编排器

## 每个示例包含

- **主程序文件** (`*.py`) - 核心实现代码
- **配置文件** (`config.yaml`) - 配置参数
- **说明文档** (`README.md`) - 详细使用说明
- **测试用例** (`test_*.py`) - 单元测试
- **需求文件** (`requirements.txt`) - 额外依赖

## 运行方式

```bash
# 进入具体示例目录
cd examples/001_basic_llm_call

# 安装依赖
pip install -r requirements.txt

# 运行示例
python main.py
```

## 框架特性展示

每个示例都专注于展示框架的特定功能：

- **模块化设计** - 可插拔的组件架构
- **多提供商支持** - OpenAI、Anthropic、DeepSeek等
- **工具集成** - Function Calling和外部API
- **状态管理** - 会话和上下文管理
- **错误处理** - 优雅的异常处理
- **监控和日志** - 完整的可观测性
- **配置管理** - 灵活的配置系统
- **测试覆盖** - 完整的测试体系

## 学习路径建议

1. **新手** - 从001-005开始，学习基础概念
2. **进阶** - 继续006-010，掌握工具集成
3. **专家** - 学习011-015，理解智能代理
4. **大师** - 挑战016-020，构建复杂系统

每个示例都可以独立运行，也可以组合使用构建更复杂的应用。