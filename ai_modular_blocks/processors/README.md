# Processors Module

文档处理器模块 - AI Modular Blocks的数据预处理层

## 🎯 职责范围

实现各种文档处理和数据预处理功能，将原始数据转换为AI系统可以处理的标准格式。

## 📁 目录组织

### 文档加载器 (Loaders)
从各种数据源加载原始文档：

```
loaders/
├── text.py        # 纯文本文件加载器
├── pdf.py         # PDF文档加载器
├── html.py        # HTML网页加载器
├── markdown.py    # Markdown文档加载器
├── office.py      # Office文档加载器（Word, Excel, PPT）
├── code.py        # 代码文件加载器
└── database.py    # 数据库记录加载器
```

### 文档分割器 (Splitters)
将大文档拆分为适合处理的小块：

```
splitters/
├── text_splitter.py      # 文本分割器
├── recursive_splitter.py # 递归字符分割器
├── semantic_splitter.py  # 语义分割器
├── code_splitter.py      # 代码分割器
└── markdown_splitter.py  # Markdown结构分割器
```

### 文档转换器 (Transformers)
对文档内容进行格式转换和清理：

```
transformers/
├── cleaner.py         # 文本清理器
├── normalizer.py      # 文本标准化器
├── extractor.py       # 关键信息提取器
├── enricher.py        # 元数据丰富器
└── formatter.py       # 格式转换器
```

### 文档过滤器 (Filters)
基于各种条件过滤和筛选文档：

```
filters/
├── content_filter.py   # 内容过滤器
├── metadata_filter.py  # 元数据过滤器
├── quality_filter.py   # 质量过滤器
└── dedup_filter.py     # 去重过滤器
```

## 🔧 核心接口

所有处理器都实现`DocumentProcessor`接口：

```python
from ai_modular_blocks.core.interfaces import DocumentProcessor
from ai_modular_blocks.core.types import DocumentList

class MyProcessor(DocumentProcessor):
    async def process(self, documents: DocumentList) -> DocumentList:
        # 实现文档处理逻辑
        processed_docs = []
        for doc in documents:
            processed_doc = await self.process_single(doc)
            processed_docs.append(processed_doc)
        return processed_docs
    
    def get_processor_name(self) -> str:
        return "my_processor"
```

## 📖 使用示例

### 文档加载和处理流水线
```python
from ai_modular_blocks.processors.loaders import PDFLoader
from ai_modular_blocks.processors.splitters import RecursiveSplitter
from ai_modular_blocks.processors.transformers import TextCleaner
from ai_modular_blocks.processors.filters import QualityFilter

# 创建处理流水线
async def process_pdf_document(file_path: str):
    # 1. 加载PDF文档
    loader = PDFLoader()
    documents = await loader.load(file_path)
    
    # 2. 清理文本
    cleaner = TextCleaner()
    documents = await cleaner.process(documents)
    
    # 3. 分割文档
    splitter = RecursiveSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = await splitter.process(documents)
    
    # 4. 质量过滤
    quality_filter = QualityFilter(
        min_length=50,
        max_length=2000
    )
    documents = await quality_filter.process(documents)
    
    return documents
```

### 批量文档处理
```python
from ai_modular_blocks.processors import ProcessingPipeline

# 定义处理流水线
pipeline = ProcessingPipeline([
    PDFLoader(),
    TextCleaner(),
    RecursiveSplitter(chunk_size=1000),
    QualityFilter(min_length=50)
])

# 批量处理文档
file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
all_documents = []

for file_path in file_paths:
    documents = await pipeline.process_file(file_path)
    all_documents.extend(documents)

print(f"处理了 {len(all_documents)} 个文档块")
```

### 自定义处理器
```python
from ai_modular_blocks.core.base import BaseDocumentProcessor
from ai_modular_blocks.core.types import VectorDocument
import re

class EmailProcessor(BaseDocumentProcessor):
    """邮件内容处理器"""
    
    def __init__(self):
        super().__init__("email_processor")
    
    async def _process_impl(self, documents: DocumentList) -> DocumentList:
        processed = []
        
        for doc in documents:
            # 提取邮件头信息
            content = doc.content
            
            # 提取发件人
            sender_match = re.search(r'From: (.+)', content)
            sender = sender_match.group(1) if sender_match else "Unknown"
            
            # 提取主题
            subject_match = re.search(r'Subject: (.+)', content)
            subject = subject_match.group(1) if subject_match else "No Subject"
            
            # 提取正文（去除邮件头）
            body_start = content.find('\n\n')
            body = content[body_start+2:] if body_start != -1 else content
            
            # 创建处理后的文档
            processed_doc = VectorDocument(
                id=doc.id,
                content=body.strip(),
                metadata={
                    **doc.metadata,
                    "sender": sender,
                    "subject": subject,
                    "content_type": "email"
                },
                content_type=doc.content_type,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            
            processed.append(processed_doc)
        
        return processed
```

## 🚀 扩展指南

### 添加新的文档加载器
1. 继承`BaseDocumentProcessor`或实现`DocumentProcessor`接口
2. 实现文档加载逻辑
3. 处理各种文件格式和编码

```python
from ai_modular_blocks.core.base import BaseDocumentProcessor

class JSONLoader(BaseDocumentProcessor):
    def __init__(self):
        super().__init__("json_loader")
    
    async def load(self, file_path: str) -> DocumentList:
        """从JSON文件加载文档"""
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                doc = VectorDocument(
                    id=f"{file_path}_{i}",
                    content=json.dumps(item, ensure_ascii=False),
                    metadata={"source": file_path, "index": i}
                )
                documents.append(doc)
        
        return documents
```

### 添加新的文档分割策略
```python
class SemanticSplitter(BaseDocumentProcessor):
    """基于语义的文档分割器"""
    
    def __init__(self, embedding_provider, similarity_threshold=0.8):
        super().__init__("semantic_splitter")
        self.embedding_provider = embedding_provider
        self.similarity_threshold = similarity_threshold
    
    async def _process_impl(self, documents: DocumentList) -> DocumentList:
        split_documents = []
        
        for doc in documents:
            # 按句子分割
            sentences = self.split_into_sentences(doc.content)
            
            # 生成句子嵌入
            embeddings = await self.embedding_provider.embed_text(sentences)
            
            # 基于语义相似性合并句子
            chunks = self.merge_by_similarity(sentences, embeddings)
            
            # 创建分割后的文档
            for i, chunk in enumerate(chunks):
                split_doc = VectorDocument(
                    id=f"{doc.id}_chunk_{i}",
                    content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "parent_id": doc.id
                    }
                )
                split_documents.append(split_doc)
        
        return split_documents
```

## 🎨 设计原则

### 1. 流水线模式
处理器可以组合成流水线，数据依次通过各个处理器：

```python
# 流水线组合
pipeline = [
    PDFLoader(),
    TextCleaner(),
    RecursiveSplitter(),
    QualityFilter()
]

# 依次处理
documents = input_documents
for processor in pipeline:
    documents = await processor.process(documents)
```

### 2. 可配置性
每个处理器都支持丰富的配置选项：

```python
splitter = RecursiveSplitter(
    chunk_size=1000,           # 块大小
    chunk_overlap=200,         # 重叠大小
    separators=['\n\n', '\n'], # 分割符优先级
    keep_separator=True        # 保留分割符
)
```

### 3. 容错性
处理器应该优雅地处理各种异常情况：

```python
async def _process_impl(self, documents: DocumentList) -> DocumentList:
    processed = []
    errors = []
    
    for doc in documents:
        try:
            processed_doc = await self.process_single(doc)
            processed.append(processed_doc)
        except Exception as e:
            # 记录错误但继续处理
            self.logger.error(f"Failed to process document {doc.id}: {e}")
            errors.append({"doc_id": doc.id, "error": str(e)})
    
    # 在metadata中记录处理统计
    if hasattr(self, 'add_processing_stats'):
        self.add_processing_stats({
            "total_docs": len(documents),
            "processed_docs": len(processed),
            "error_count": len(errors),
            "errors": errors
        })
    
    return processed
```

## 🔧 性能优化

### 并行处理
```python
import asyncio

async def process_documents_parallel(self, documents: DocumentList) -> DocumentList:
    """并行处理文档以提高性能"""
    semaphore = asyncio.Semaphore(10)  # 限制并发数
    
    async def process_with_semaphore(doc):
        async with semaphore:
            return await self.process_single(doc)
    
    tasks = [process_with_semaphore(doc) for doc in documents]
    processed_docs = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤异常结果
    valid_docs = [doc for doc in processed_docs if not isinstance(doc, Exception)]
    return valid_docs
```

### 内存优化
```python
async def process_large_documents(self, documents: DocumentList) -> DocumentList:
    """流式处理大文档集合"""
    processed = []
    
    # 分批处理以控制内存使用
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_result = await self.process_batch(batch)
        processed.extend(batch_result)
        
        # 可选：触发垃圾回收
        if i % 1000 == 0:
            import gc
            gc.collect()
    
    return processed
```

## 🎯 最佳实践

1. **单一职责** - 每个处理器只做一件事
2. **幂等操作** - 重复处理应该产生相同结果
3. **状态保存** - 支持处理过程的状态保存和恢复
4. **进度追踪** - 长时间处理提供进度信息
5. **资源清理** - 及时释放文件句柄和内存资源

## 🔍 调试和监控

### 处理器链调试
```python
from ai_modular_blocks.utils.logging import get_logger

logger = get_logger(__name__)

async def debug_pipeline(documents: DocumentList, processors: List[DocumentProcessor]):
    """调试处理器流水线"""
    current_docs = documents
    
    for i, processor in enumerate(processors):
        logger.info(f"Step {i+1}: {processor.get_processor_name()}")
        logger.info(f"Input: {len(current_docs)} documents")
        
        current_docs = await processor.process(current_docs)
        
        logger.info(f"Output: {len(current_docs)} documents")
        
        if len(current_docs) == 0:
            logger.warning(f"No documents after {processor.get_processor_name()}")
            break
    
    return current_docs
```

### 性能监控
```python
from ai_modular_blocks.utils.monitoring import monitor

class MonitoredProcessor(BaseDocumentProcessor):
    
    @monitor.time_operation("document_processing")
    @monitor.count_calls("processor_calls")
    async def process(self, documents: DocumentList) -> DocumentList:
        return await super().process(documents)
```
