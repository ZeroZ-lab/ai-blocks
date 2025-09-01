# 014 - 自我改进代理

展示如何创建能够从经验中学习并持续改进的智能代理。

## 特点

- **性能反思**: 执行后自动分析表现和改进点
- **模式学习**: 识别和记录成功的执行模式  
- **知识积累**: 建立持续增长的知识库
- **纯Python**: 用标准数据结构实现学习机制

## 核心功能

1. **反思机制**: 每次任务后自动评估性能
2. **模式识别**: 识别并记录成功策略
3. **知识库**: 积累可复用的经验和技巧
4. **性能跟踪**: 监控改进趋势

## 使用方法

```bash
export OPENAI_API_KEY="your-key-here"
python main.py
```

## 自我改进循环

```python
agent = SelfImprovingAgent("openai")

# 执行任务并自动改进
result = await agent.execute_task_with_reflection("计算投资收益")

# 查看学习成果
summary = agent.get_improvement_summary()
```

## 关键概念

- **学习驱动**: 从每次执行中提取经验
- **模式匹配**: 基于历史成功案例优化策略
- **持续改进**: 性能指标持续跟踪和提升