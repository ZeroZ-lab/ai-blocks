# Utils Module

工具模块 - AI Modular Blocks的辅助功能层

## 🎯 职责范围

提供系统运行所需的各种辅助工具和基础设施功能，包括缓存、日志、监控等横切关注点。

## 📁 目录组织

### `caching/` - 缓存系统
提供多种缓存策略和存储后端：

```
caching/
├── memory.py      # 内存缓存实现
├── redis.py       # Redis缓存实现
├── file.py        # 文件系统缓存
├── manager.py     # 缓存管理器
└── strategies.py  # 缓存策略（LRU、TTL等）
```

**核心功能**: 响应缓存、中间结果缓存、会话状态缓存

### `logging/` - 日志系统
结构化日志记录和分析：

```
logging/
├── formatters.py  # 日志格式化器
├── handlers.py    # 日志处理器
├── filters.py     # 日志过滤器
└── config.py      # 日志配置管理
```

**核心功能**: 结构化日志、性能追踪、错误分析、安全审计

### `monitoring/` - 监控系统
系统性能和健康状况监控：

```
monitoring/
├── metrics.py     # 指标收集
├── health.py      # 健康检查
├── profiling.py   # 性能分析
└── alerts.py      # 告警系统
```

**核心功能**: 性能指标、资源监控、异常告警、SLA监控

## 🔧 核心特性

### 1. 统一的缓存接口
所有缓存实现都遵循统一接口：

```python
from ai_modular_blocks.utils.caching import CacheManager
from ai_modular_blocks.core.interfaces import CacheProvider

# 支持多种缓存后端
cache: CacheProvider = CacheManager.get_cache("redis")

# 统一的缓存操作
await cache.set("key", "value", ttl=3600)
value = await cache.get("key")
```

### 2. 结构化日志记录
提供丰富的上下文信息和查询能力：

```python
from ai_modular_blocks.utils.logging import get_logger

logger = get_logger(__name__)

# 结构化日志
logger.info(
    "LLM request completed",
    extra={
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "tokens": 150,
        "duration_ms": 1200,
        "success": True
    }
)
```

### 3. 实时监控指标
自动收集系统关键指标：

```python
from ai_modular_blocks.utils.monitoring import metrics

# 自动指标收集
@metrics.time_operation("llm_chat_completion")
@metrics.count_calls("llm_requests")
async def chat_completion(self, messages, model):
    # 业务逻辑
    pass

# 手动指标记录
metrics.increment("custom_counter", tags={"provider": "openai"})
metrics.gauge("active_connections", 42)
```

## 📖 使用示例

### 缓存使用示例
```python
from ai_modular_blocks.utils.caching import CacheManager
from ai_modular_blocks.core.types import LLMResponse

# 配置缓存
cache_config = {
    "type": "redis",
    "url": "redis://localhost:6379",
    "default_ttl": 3600
}

cache = CacheManager.create_cache(cache_config)

# 缓存LLM响应
async def cached_chat_completion(messages, model):
    cache_key = f"llm:{model}:{hash(str(messages))}"
    
    # 尝试从缓存获取
    cached_response = await cache.get(cache_key)
    if cached_response:
        return LLMResponse.from_dict(cached_response)
    
    # 调用LLM
    response = await llm.chat_completion(messages, model)
    
    # 缓存结果
    await cache.set(cache_key, response.to_dict(), ttl=1800)
    
    return response
```

### 监控装饰器使用
```python
from ai_modular_blocks.utils.monitoring import monitor

class MyLLMProvider(BaseLLMProvider):
    
    @monitor.time_and_count("chat_completion")
    @monitor.track_errors()
    async def chat_completion(self, messages, model, **kwargs):
        # 自动记录调用次数、执行时间、错误率
        return await self._chat_completion_impl(messages, model, **kwargs)
    
    @monitor.health_check("llm_provider")
    async def health_check(self):
        # 自动记录健康状态
        return await self._perform_health_check()
```

### 日志上下文管理
```python
from ai_modular_blocks.utils.logging import LogContext

async def process_request(request_id: str):
    with LogContext(request_id=request_id, user_id="user123"):
        logger.info("Processing request")  # 自动包含context
        
        result = await some_operation()
        
        logger.info("Request completed", extra={"result_size": len(result)})
```

## 🚀 扩展指南

### 添加新的缓存后端
1. 实现`CacheProvider`接口
2. 在`caching/`目录添加实现
3. 注册到`CacheManager`

```python
# utils/caching/mongodb.py
from ai_modular_blocks.core.interfaces import CacheProvider

class MongoDBCache(CacheProvider):
    async def get(self, key: str) -> Optional[Any]:
        # MongoDB缓存实现
        pass
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        # 实现set方法
        pass
```

### 添加自定义监控指标
```python
from ai_modular_blocks.utils.monitoring import MetricsCollector

# 注册自定义指标
metrics = MetricsCollector()
metrics.register_counter("custom_events", "Custom event counter")
metrics.register_histogram("response_sizes", "Response size distribution")

# 使用自定义指标
metrics.increment("custom_events", tags={"event_type": "user_action"})
metrics.observe("response_sizes", response_size)
```

### 自定义日志处理器
```python
from ai_modular_blocks.utils.logging import BaseLogHandler

class SlackLogHandler(BaseLogHandler):
    """发送重要日志到Slack"""
    
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.send_to_slack(record)
```

## 🎨 设计原则

### 1. 非侵入性
工具功能不应该侵入业务逻辑：

```python
# ✅ 好的设计 - 装饰器/上下文管理器
@monitor.track_performance
async def business_function():
    # 纯业务逻辑，不包含监控代码
    pass

# ❌ 坏的设计 - 侵入性代码
async def business_function():
    start_time = time.time()  # 监控代码侵入
    try:
        # 业务逻辑
        result = do_something()
        monitor.record_success(time.time() - start_time)
        return result
    except Exception as e:
        monitor.record_error(e)
        raise
```

### 2. 配置驱动
所有工具功能都可以通过配置启用/禁用：

```python
# 通过配置控制功能
if config.monitoring.enabled:
    enable_monitoring()

if config.caching.enabled:
    enable_caching(config.caching)
```

### 3. 异步优先
所有I/O操作都是异步的，避免阻塞：

```python
# 异步缓存操作
async def get_or_compute(key: str, compute_func):
    value = await cache.get(key)
    if value is None:
        value = await compute_func()
        await cache.set(key, value)
    return value
```

## 🔧 性能优化

### 缓存策略
- **多层缓存** - 内存 + Redis的层次化缓存
- **智能失效** - 基于依赖关系的缓存失效
- **预加载** - 热点数据的预先加载
- **压缩存储** - 大对象的压缩存储

### 监控开销最小化
- **采样监控** - 高频操作的采样记录
- **异步写入** - 监控数据的异步批量写入
- **指标聚合** - 本地聚合后批量上报
- **条件监控** - 仅在需要时启用详细监控

## 🛡️ 安全考虑

### 日志安全
- **敏感信息过滤** - 自动过滤API密钥等敏感信息
- **日志加密** - 敏感日志的加密存储
- **访问控制** - 基于角色的日志访问控制

### 缓存安全
- **数据加密** - 缓存数据的透明加密
- **访问隔离** - 不同租户的缓存隔离
- **安全清理** - 敏感数据的安全清理

## 🎯 最佳实践

1. **渐进式启用** - 从基础功能开始，逐步启用高级功能
2. **配置外化** - 所有配置都可以通过环境变量或配置文件管理
3. **故障隔离** - 工具功能故障不应影响业务功能
4. **性能监控** - 持续监控工具本身的性能开销
5. **版本兼容** - 工具配置和数据格式的向后兼容
