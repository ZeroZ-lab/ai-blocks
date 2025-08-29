"""
配置示例文件

复制此文件为config.py并填入真实的API keys
"""

import os

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-openai-api-key-here")

# Anthropic配置 (可选)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")

# 默认模型配置
DEFAULT_LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7
}
