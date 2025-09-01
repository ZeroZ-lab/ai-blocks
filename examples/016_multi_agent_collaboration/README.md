# 016 - 多代理协作

展示如何创建多个智能代理协同工作完成复杂项目。

## 特点

- **角色专门化**: 不同代理承担不同专业角色
- **消息通信**: 代理间通过消息进行协作
- **项目协调**: 项目经理代理负责任务分配和进度管理
- **纯Python**: 用面向对象设计实现代理协作

## 代理类型

1. **ProjectManager**: 项目协调和任务分配
2. **DataAnalyst**: 数据分析和统计计算  
3. **TechnicalExpert**: 技术方案设计和实现

## 使用方法

```bash
export OPENAI_API_KEY="your-key-here"
python main.py
```

## 协作模式

```python
# 创建多代理系统
system = MultiAgentSystem()
system.add_agent(ProjectManager("openai"))
system.add_agent(DataAnalyst("openai"))

# 启动协作项目
result = await system.start_collaboration("开发数据分析系统", ["ProjectManager", "DataAnalyst"])
```

## 关键概念

- **专业分工**: 每个代理专注特定领域
- **消息协议**: 标准化的代理间通信
- **协作编排**: 系统级的协作管理