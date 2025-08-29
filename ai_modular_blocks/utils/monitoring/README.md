# Monitoring Module

监控系统实现

## 🎯 模块说明

提供系统性能监控、健康检查、指标收集、告警通知等功能，确保AI应用的可观测性。

## 📁 文件组织

### `metrics.py` - 指标收集
- **Counter**: 计数器指标
- **Gauge**: 仪表盘指标  
- **Histogram**: 分布指标
- **Timer**: 时间指标

### `health.py` - 健康检查
- **HealthChecker**: 健康检查器
- **ComponentHealth**: 组件健康状态
- **HealthEndpoint**: HTTP健康检查端点

### `profiling.py` - 性能分析
- **ProfilerManager**: 性能分析管理
- **MemoryProfiler**: 内存使用分析
- **CPUProfiler**: CPU使用分析

### `alerts.py` - 告警系统
- **AlertManager**: 告警管理器
- **AlertRule**: 告警规则
- **NotificationChannel**: 通知渠道

## 📖 使用示例

```python
from ai_modular_blocks.utils.monitoring import metrics, HealthChecker

# 装饰器监控
@metrics.time_operation("llm_chat_completion")
@metrics.count_calls("llm_requests")
async def chat_completion(self, messages, model):
    # 业务逻辑
    pass

# 手动指标记录
metrics.increment("api_calls", tags={"endpoint": "/chat"})
metrics.gauge("active_connections", 42)
metrics.histogram("response_time", 250)

# 健康检查
health_checker = HealthChecker()
health_checker.register_check("database", check_db_connection)
health_checker.register_check("redis", check_redis_connection)

health_status = await health_checker.check_all()
print(f"系统健康状态: {health_status.overall_status}")
```
