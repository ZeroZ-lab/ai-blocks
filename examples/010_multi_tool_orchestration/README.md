# 010 - 多工具协调

展示如何优雅地协调多个独立工具来完成复杂的工作流程。

## 特点

- **工作流编排**: 使用纯Python协调多个工具
- **错误处理**: 优雅处理每个步骤的错误
- **状态跟踪**: 记录工作流执行状态
- **结果持久化**: 自动保存分析结果

## 功能

1. **DataAnalysisWorkflow**: 金融数据分析工作流
   - 多源数据收集 (文件 + Web API)
   - 数学计算处理
   - LLM智能分析
   - 结果保存

2. **ResearchPipeline**: 自动化研究管道
   - 研究计划生成
   - 信息搜索执行
   - 数据分析处理
   - 报告自动生成

## 使用方法

```bash
# 设置环境变量
export OPENAI_API_KEY="your-key-here"

# 运行示例
python main.py
```

## 工作流特点

### 数据分析工作流
```python
# 完全用户自定义的工作流
workflow = DataAnalysisWorkflow("openai")
result = await workflow.analyze_financial_data(data_sources)
```

### 研究管道
```python
# 纯Python的研究自动化
pipeline = ResearchPipeline("openai") 
result = await pipeline.conduct_research("AI应用")
```

## 关键概念

- **工具独立性**: 每个工具都可以单独使用
- **自由组合**: 用户完全控制工具的组合方式
- **纯Python**: 没有特殊DSL，全部是标准Python代码
- **错误恢复**: 单个工具失败不会影响整个流程

## 扩展想法

- 添加并行处理支持
- 实现工作流可视化
- 添加更多数据源连接器
- 支持工作流模板化
- 实现结果缓存机制