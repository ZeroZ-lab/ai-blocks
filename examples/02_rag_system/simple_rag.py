#!/usr/bin/env python3
"""
简单RAG (检索增强生成) 示例

展示如何构建一个基础的RAG系统：
1. 文档存储到向量数据库
2. 用户提问时检索相关文档  
3. 将检索结果作为上下文传给LLM生成回答

这是最实用的AI应用模式之一。
"""

import asyncio
import os
from ai_modular_blocks.providers.llm import LLMProviderFactory
from ai_modular_blocks.providers.vectorstores import VectorStoreFactory
from ai_modular_blocks.core.types import (
    LLMConfig, VectorStoreConfig, ChatMessage, VectorDocument
)


# 示例文档数据 - 关于Python编程的知识
SAMPLE_DOCS = [
    {
        "content": "Python是一种高级编程语言，具有简洁易读的语法。它由Guido van Rossum于1991年创建。",
        "metadata": {"topic": "python_basics", "source": "intro"}
    },
    {
        "content": "Python支持多种编程范式，包括面向对象、函数式和过程式编程。",
        "metadata": {"topic": "python_paradigms", "source": "concepts"}
    },
    {
        "content": "pip是Python的包管理器，用于安装和管理Python包。使用pip install package_name来安装包。",
        "metadata": {"topic": "python_tools", "source": "tools"}
    },
    {
        "content": "虚拟环境是Python开发的最佳实践，可以使用venv或conda来创建隔离的Python环境。",
        "metadata": {"topic": "python_environment", "source": "best_practices"}
    }
]


async def setup_rag_system():
    """初始化RAG系统"""
    
    # 1. 初始化工厂
    LLMProviderFactory.initialize()
    VectorStoreFactory.initialize()
    
    # 2. 检查依赖
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置OPENAI_API_KEY环境变量")
        return None, None
    
    # 3. 创建LLM provider
    llm_config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=200,
        temperature=0.3  # 较低温度保证回答准确性
    )
    llm = LLMProviderFactory.create_provider("openai", llm_config)
    
    # 4. 创建向量存储（使用ChromaDB，本地运行）
    vector_config = VectorStoreConfig(
        provider="chroma",
        collection_name="python_knowledge",
        persist_directory="./chroma_db"  # 本地存储
    )
    vector_store = VectorStoreFactory.create_provider("chroma", vector_config)
    
    return llm, vector_store


async def load_documents(vector_store):
    """加载示例文档到向量数据库"""
    
    print("📚 正在加载文档到向量数据库...")
    
    # 转换为VectorDocument格式
    docs = []
    for i, doc in enumerate(SAMPLE_DOCS):
        vector_doc = VectorDocument(
            id=f"doc_{i}",
            content=doc["content"],
            metadata=doc["metadata"],
            # 注意：这里embedding会由vector store自动生成
        )
        docs.append(vector_doc)
    
    # 批量添加文档
    await vector_store.add_documents(docs)
    print(f"✅ 已加载 {len(docs)} 个文档")


async def rag_query(question: str, llm, vector_store):
    """执行RAG查询"""
    
    print(f"\n❓ 用户问题: {question}")
    
    # 1. 检索相关文档
    print("🔍 正在检索相关文档...")
    search_results = await vector_store.search(
        query=question,
        limit=2,  # 只取最相关的2个文档
        threshold=0.5  # 相似度阈值
    )
    
    if not search_results.documents:
        print("❌ 没有找到相关文档")
        return
    
    # 2. 构建上下文
    context = "\n".join([
        f"文档{i+1}: {doc.content}" 
        for i, doc in enumerate(search_results.documents)
    ])
    
    print(f"📄 找到 {len(search_results.documents)} 个相关文档")
    
    # 3. 构造提示词
    prompt = f"""基于以下文档内容回答用户问题，如果文档中没有相关信息，请说明无法回答。

文档内容:
{context}

用户问题: {question}

请简洁准确地回答:"""

    # 4. 生成回答
    messages = [ChatMessage(role="user", content=prompt)]
    response = await llm.generate(messages)
    
    print(f"🤖 RAG回答: {response.content}")
    return response.content


async def interactive_rag_demo():
    """交互式RAG演示"""
    
    print("=== AI Modular Blocks - 简单RAG系统演示 ===")
    
    # 初始化系统
    llm, vector_store = await setup_rag_system()
    if not llm or not vector_store:
        return
    
    # 加载文档
    await load_documents(vector_store)
    
    # 预设问题演示
    demo_questions = [
        "Python是什么时候创建的？",
        "如何安装Python包？",
        "Python支持哪些编程范式？",
        "Java和C++的区别是什么？"  # 这个问题文档中没有答案
    ]
    
    print("\n🎯 开始演示预设问题:")
    for question in demo_questions:
        await rag_query(question, llm, vector_store)
        print("-" * 50)
    
    print("\n✨ RAG系统演示完成！")
    print("💡 这个示例展示了:")
    print("   1. 如何将文档存储到向量数据库")
    print("   2. 如何根据问题检索相关文档")
    print("   3. 如何将检索结果作为上下文生成回答")


if __name__ == "__main__":
    asyncio.run(interactive_rag_demo())
