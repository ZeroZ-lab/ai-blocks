# Logging Module

日志系统实现

## 🎯 模块说明

提供结构化日志记录、性能追踪、错误分析等功能，支持多种输出格式和处理器。

## 📁 文件组织

### `formatters.py` - 日志格式化器
- **JSONFormatter**: 结构化JSON日志
- **ColoredFormatter**: 彩色终端输出
- **CompactFormatter**: 紧凑格式日志

### `handlers.py` - 日志处理器
- **AsyncFileHandler**: 异步文件写入
- **RotatingHandler**: 文件轮转处理
- **SlackHandler**: Slack通知集成
- **ElasticsearchHandler**: 日志搜索集成

### `filters.py` - 日志过滤器
- **SensitiveDataFilter**: 敏感信息过滤
- **LevelFilter**: 日志级别过滤
- **RateLimitFilter**: 频率限制过滤

### `config.py` - 日志配置管理
- **LoggingConfig**: 日志配置类
- **setup_logging()**: 日志初始化
- **get_logger()**: 获取日志器

## 📖 使用示例

```python
from ai_modular_blocks.utils.logging import get_logger, LogContext

# 获取日志器
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

# 上下文日志
with LogContext(request_id="req123", user_id="user456"):
    logger.info("Processing request")  # 自动包含context
    # ... 业务逻辑
    logger.info("Request completed")
```
