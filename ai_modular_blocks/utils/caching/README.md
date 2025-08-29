# Caching Module

缓存系统实现

## 🎯 模块说明

提供多种缓存后端和策略，实现`CacheProvider`接口，支持LLM响应缓存、向量搜索缓存等场景。

## 📁 文件组织

### `memory.py` - 内存缓存
- **特点**: 快速访问、进程内共享
- **适用**: 开发测试、单机部署
- **实现**: 基于Python字典+LRU策略

### `redis.py` - Redis缓存  
- **特点**: 分布式、持久化、高性能
- **适用**: 生产环境、多实例部署
- **实现**: Redis客户端封装

### `file.py` - 文件系统缓存
- **特点**: 持久化、无依赖、简单
- **适用**: 离线环境、临时缓存
- **实现**: 文件系统目录结构

### `manager.py` - 缓存管理器
- **功能**: 统一缓存接口、自动选择后端
- **特点**: 配置驱动、热切换支持

### `strategies.py` - 缓存策略
- **LRU**: 最近最少使用
- **TTL**: 时间过期策略  
- **LFU**: 最少使用频率

## 📖 使用示例

```python
from ai_modular_blocks.utils.caching import CacheManager

# 创建缓存管理器
cache_config = {
    "type": "redis",
    "url": "redis://localhost:6379",
    "default_ttl": 3600
}

cache = CacheManager.create_cache(cache_config)

# 基础操作
await cache.set("key", "value", ttl=300)
value = await cache.get("key")
await cache.delete("key")

# LLM响应缓存
async def cached_llm_call(messages, model):
    cache_key = f"llm:{model}:{hash(str(messages))}"
    
    # 尝试缓存
    cached = await cache.get(cache_key)
    if cached:
        return LLMResponse.from_dict(cached)
    
    # 调用LLM
    response = await llm.chat_completion(messages, model)
    
    # 缓存结果
    await cache.set(cache_key, response.to_dict(), ttl=1800)
    return response
```
