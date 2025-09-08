# TODO: AI Modular Blocks 优化计划

## M1（本周，稳定性与一致性）
- [ ] 统一 DeepSeek 默认行为与示例
  - [ ] 显式将示例默认 `provider` 设为 `deepseek`（或基于环境自动选择并打印所用 provider）
  - [ ] 文档中强调 DeepSeek 为示例默认（含 `.env` 模板）
- [ ] 加入统一的重试与超时
  - [ ] 在 `BaseLLMProvider` 增加 `_call_with_retry`（基于 `tenacity` 指数退避、最大重试、抖动）
  - [ ] 为工具层（`WebClient`）增加连接/读超时与重试策略（对 5xx/超时重试）
- [ ] 示例非交互化（避免CI阻塞）
  - [ ] 对所有示例的交互输入加 `sys.stdin.isatty()` 守卫（006/007/009/010/011/012/013/014/015/016/020）
- [ ] WebClient 稳健性
  - [ ] 保留通用 UA/Accept 头，返回 `data`（JSON）和 `content`（文本）
  - [ ] 为 008 增加“API优先”选项（如 Wikipedia REST），并在 README 说明站点差异
- [ ] 测试与用例（最小集）
  - [ ] Provider 工厂与 DeepSeek base_url 归一化单测
  - [ ] `generate_from_messages`/`stream_generate` 单测（Mock）
  - [ ] `FileOperations`（异步）与 `WebClient` 单测（Mock）
- [ ] 文档/工作流
  - [ ] README 增补 uv 指南（`uv sync`、`uv run`），并更新 Quickstart 与目录一致
  - [ ] `examples/run_all.sh` 已改为 uv，增加运行说明与失败排查指引

## M2（下周，可观测性与安全）
- [ ] 指标与日志
  - [ ] 在 Provider 入口埋点 Prometheus 指标
    - [ ] 计数器 `llm_requests_total{provider,model,result}`
    - [ ] 直方图 `llm_request_duration_seconds{provider,model}`
    - [ ] 计数器 `tool_requests_total{name,result}`
  - [ ] 结构化日志 + request_id 贯穿
  - [ ] 可选 `/metrics` 端点 Demo
- [ ] 安全计算器
  - [ ] 用 AST/安全表达式替代 `eval`（严格白名单）
- [ ] CI（GitHub Actions + uv）
  - [ ] 任务：ruff、mypy、pytest（核心单测 + 可选集成）
  - [ ] 精选示例烟测（001/002/003/004/005 与 008 的 API 模式）
- [ ] 运行器增强
  - [ ] `run_all.sh`/Python 驱动为每个示例加超时（避免长时间挂起）

## M3（后续，性能与拓展）
- [ ] 缓存层（可选：内存/Redis），为 LLM 响应和 Web 检索提供装饰器
- [ ] 断路器/限速
  - [ ] 针对连续 429/5xx 的快速失败和恢复策略
  - [ ] 并发节流（每 provider 的 Semaphore）
- [ ] 覆盖更多 Provider/工具
  - [ ] 增加/完善 Embeddings、VectorStore 等（按路线图推进）
- [ ] 文档增强
  - [ ] 监控/告警最佳实践
  - [ ] 生产部署清单（超时、重试、限流、日志、指标、健康检查）

## 文件与代码改动清单
- [ ] `ai_modular_blocks/core/base.py`：重试/超时封装、指标埋点、统一入口
- [ ] `ai_modular_blocks/tools/web_client.py`：超时、重试、默认请求头、返回结构
- [ ] `ai_modular_blocks/tools/calculator.py`：AST 安全表达式
- [ ] `examples/*/main.py`：非交互守卫、默认 provider、说明输出
- [ ] `examples/run_all.sh`：uv 运行、超时控制（或改为 Python 驱动）
- [ ] 文档：`README.md`、`examples/README.md`、`docs/` 可观测性/uv 指南

## 交付与验收标准
- [ ] 所有示例可在含 `DEEPSEEK_API_KEY` 的环境下通过 `uv run` 非交互运行（少量对外网站不稳定除外，并有降级/说明）
- [ ] 单测覆盖核心路径（>80% 的 core、>90% 的 tools 基础逻辑）
- [ ] 关键指标可在本地 `/metrics` 导出并被 Prometheus 抓取
- [ ] README 与实际实现一致，含 uv-first 的快速上手

## 快速命令（uv）
- `uv sync --no-dev`
- 运行示例（单个）: `uv run -q python examples/001_basic_llm_call/main.py`
- 批量示例: `bash examples/run_all.sh`
- 代码质量: `uvx ruff check . && uvx ruff format . && uvx mypy .`
- 测试: `uv run -q pytest -q`

