#!/usr/bin/env python3

import asyncio
import os
import sys
sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import WebClient

class WebSearchAssistant:
    """
    网页搜索助手 - 结合LLM和Web客户端工具
    
    用户完全自由的实现方式，框架只提供基础构建块
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.web_client = WebClient()
    
    async def search_and_analyze(self, query: str, urls: list[str]) -> dict:
        """搜索多个URL并让LLM分析内容"""
        
        # 1. 获取网页内容
        print(f"🔍 正在搜索: {query}")
        web_results = []
        
        for url in urls:
            print(f"📄 获取: {url}")
            result = await self.web_client.fetch(url)
            if result["success"]:
                web_results.append({
                    "url": url,
                    "content": result["content"][:2000],  # 限制长度
                    "title": result.get("title", "未知标题")
                })
        
        if not web_results:
            return {"error": "没有成功获取任何网页内容"}
        
        # 2. 构造分析提示
        content_summary = "\n\n".join([
            f"网页 {i+1}: {result['title']}\nURL: {result['url']}\n内容摘要: {result['content']}"
            for i, result in enumerate(web_results)
        ])
        
        prompt = f"""
基于以下搜索到的网页内容，回答用户问题: {query}

搜索结果:
{content_summary}

请提供一个准确、有用的答案，并引用相关来源。
"""
        
        # 3. LLM分析
        print("🤖 正在分析搜索结果...")
        response = await self.llm.generate(prompt)
        
        return {
            "query": query,
            "sources": [r["url"] for r in web_results],
            "analysis": response["content"],
            "raw_results": web_results
        }
    
    async def research_topic(self, topic: str) -> dict:
        """研究某个主题，自动搜索相关资源"""
        
        # 1. 让LLM生成搜索策略
        strategy_prompt = f"""
我想研究主题: {topic}

请为这个研究主题推荐3-5个权威的网站URL，用于深入了解。
只返回URL列表，每行一个，不需要其他说明。
"""
        
        strategy_response = await self.llm.generate(strategy_prompt)
        
        # 2. 解析推荐的URL
        suggested_urls = [
            line.strip() 
            for line in strategy_response["content"].split('\n') 
            if line.strip() and line.strip().startswith('http')
        ]
        
        if not suggested_urls:
            # 如果LLM没有提供URL，使用一些通用的研究网站
            suggested_urls = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://www.nature.com",
                "https://arxiv.org"
            ]
        
        # 3. 执行搜索和分析
        return await self.search_and_analyze(topic, suggested_urls[:3])

async def main():
    """演示网页搜索工具的使用"""
    
    assistant = WebSearchAssistant("openai")
    
    # 示例1: 指定URL搜索
    print("=== 示例1: 指定URL搜索 ===")
    urls = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]
    
    result1 = await assistant.search_and_analyze(
        "什么是机器学习和深度学习的主要区别？", 
        urls
    )
    
    if "error" not in result1:
        print(f"🔍 查询: {result1['query']}")
        print(f"📚 来源: {', '.join(result1['sources'])}")
        print(f"📝 分析: {result1['analysis']}")
    else:
        print(f"❌ 错误: {result1['error']}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 主题研究
    print("=== 示例2: 主题研究 ===")
    result2 = await assistant.research_topic("量子计算的最新进展")
    
    if "error" not in result2:
        print(f"🔬 研究主题: {result2['query']}")
        print(f"📚 参考来源: {', '.join(result2['sources'])}")
        print(f"📋 研究报告: {result2['analysis']}")
    else:
        print(f"❌ 错误: {result2['error']}")

if __name__ == "__main__":
    asyncio.run(main())