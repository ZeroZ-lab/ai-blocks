#!/usr/bin/env python3

import asyncio
import os
import sys
sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import FileOperations

class CodeAnalysisAssistant:
    """
    代码分析助手 - 结合LLM和文件操作工具
    
    展示如何用纯Python组合不同工具来分析代码库
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.file_ops = FileOperations()
    
    async def analyze_codebase(self, directory: str) -> dict:
        """分析代码库结构和内容"""
        
        print(f"📂 正在分析代码库: {directory}")
        
        # 1. 列出所有Python文件
        python_files = []
        list_result = await self.file_ops.list_files(directory)
        
        if not list_result["success"]:
            return {"error": f"无法访问目录: {list_result['error']}"}
        
        for file_path in list_result["files"]:
            if file_path.endswith('.py'):
                python_files.append(file_path)
        
        if not python_files:
            return {"error": "没有找到Python文件"}
        
        print(f"🐍 找到 {len(python_files)} 个Python文件")
        
        # 2. 读取文件内容
        file_contents = {}
        total_lines = 0
        
        for file_path in python_files[:10]:  # 限制文件数量
            read_result = await self.file_ops.read_file(file_path)
            if read_result["success"]:
                content = read_result["content"]
                file_contents[file_path] = content
                total_lines += len(content.split('\n'))
        
        # 3. LLM分析代码库
        files_summary = "\n\n".join([
            f"文件: {path}\n```python\n{content[:1000]}{'...' if len(content) > 1000 else ''}\n```"
            for path, content in file_contents.items()
        ])
        
        analysis_prompt = f"""
请分析这个Python代码库:

总计 {len(python_files)} 个Python文件，{total_lines} 行代码

主要文件内容:
{files_summary}

请提供以下分析:
1. 代码库的主要功能和目的
2. 架构设计特点
3. 代码质量评估
4. 可能的改进建议

请用中文回答，保持简洁但全面。
"""
        
        print("🤖 正在分析代码...")
        analysis = await self.llm.generate(analysis_prompt)
        
        return {
            "directory": directory,
            "total_files": len(python_files),
            "total_lines": total_lines,
            "analyzed_files": list(file_contents.keys()),
            "analysis": analysis["content"],
            "file_list": python_files
        }
    
    async def refactor_file(self, file_path: str, requirements: str) -> dict:
        """重构指定文件"""
        
        print(f"🔧 正在重构文件: {file_path}")
        
        # 1. 读取原文件
        read_result = await self.file_ops.read_file(file_path)
        if not read_result["success"]:
            return {"error": f"无法读取文件: {read_result['error']}"}
        
        original_content = read_result["content"]
        
        # 2. LLM生成重构代码
        refactor_prompt = f"""
请根据以下要求重构这个Python文件:

重构要求: {requirements}

原始代码:
```python
{original_content}
```

请提供重构后的完整代码，保持功能不变但改进代码质量。
只返回重构后的代码，不要添加额外说明。
"""
        
        print("🤖 正在生成重构代码...")
        refactored_response = await self.llm.generate(refactor_prompt)
        
        # 3. 创建备份并写入新代码
        backup_path = f"{file_path}.backup"
        backup_result = await self.file_ops.write_file(backup_path, original_content)
        
        if not backup_result["success"]:
            return {"error": f"无法创建备份: {backup_result['error']}"}
        
        # 4. 写入重构后的代码
        refactored_code = refactored_response["content"]
        
        # 清理代码块标记
        if refactored_code.startswith('```python'):
            refactored_code = refactored_code[9:]
        if refactored_code.endswith('```'):
            refactored_code = refactored_code[:-3]
        refactored_code = refactored_code.strip()
        
        write_result = await self.file_ops.write_file(file_path, refactored_code)
        
        if not write_result["success"]:
            return {"error": f"无法写入文件: {write_result['error']}"}
        
        return {
            "file_path": file_path,
            "backup_path": backup_path,
            "original_lines": len(original_content.split('\n')),
            "refactored_lines": len(refactored_code.split('\n')),
            "requirements": requirements,
            "success": True
        }

class DocumentationGenerator:
    """文档生成器 - 自动为代码生成文档"""
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.file_ops = FileOperations()
    
    async def generate_readme(self, directory: str) -> dict:
        """为项目生成README.md"""
        
        # 1. 分析项目结构
        list_result = await self.file_ops.list_files(directory)
        if not list_result["success"]:
            return {"error": f"无法访问目录: {list_result['error']}"}
        
        # 2. 读取关键文件
        key_files = {}
        for filename in ['main.py', '__init__.py', 'setup.py', 'pyproject.toml']:
            file_path = os.path.join(directory, filename)
            read_result = await self.file_ops.read_file(file_path)
            if read_result["success"]:
                key_files[filename] = read_result["content"][:2000]
        
        # 3. 生成README
        files_info = "\n".join([f"{name}: {content[:500]}..." for name, content in key_files.items()])
        
        readme_prompt = f"""
基于以下项目信息生成一个专业的README.md文件:

项目目录: {directory}
文件列表: {', '.join(list_result['files'][:20])}

关键文件内容:
{files_info}

请生成一个包含以下部分的README.md:
1. 项目标题和简介
2. 功能特点
3. 安装方法
4. 使用示例
5. 项目结构
6. 贡献指南

使用Markdown格式，保持专业和清晰。
"""
        
        readme_response = await self.llm.generate(readme_prompt)
        
        # 4. 写入README文件
        readme_path = os.path.join(directory, "README.md")
        write_result = await self.file_ops.write_file(readme_path, readme_response["content"])
        
        return {
            "readme_path": readme_path,
            "success": write_result["success"],
            "content": readme_response["content"][:500] + "...",
            "analyzed_files": list(key_files.keys())
        }

async def main():
    """演示文件操作工具的使用"""
    
    # 示例1: 代码库分析
    print("=== 示例1: 代码库分析 ===")
    analyzer = CodeAnalysisAssistant("openai")
    
    # 分析当前项目的ai_modular_blocks目录
    analysis_result = await analyzer.analyze_codebase("../../ai_modular_blocks")
    
    if "error" not in analysis_result:
        print(f"📊 分析结果:")
        print(f"  目录: {analysis_result['directory']}")
        print(f"  文件数: {analysis_result['total_files']}")
        print(f"  代码行数: {analysis_result['total_lines']}")
        print(f"🔍 代码分析:\n{analysis_result['analysis'][:500]}...")
    else:
        print(f"❌ 分析失败: {analysis_result['error']}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 文档生成
    print("=== 示例2: 自动文档生成 ===")
    doc_gen = DocumentationGenerator("openai")
    
    readme_result = await doc_gen.generate_readme("../../ai_modular_blocks")
    
    if readme_result["success"]:
        print(f"📝 README生成成功: {readme_result['readme_path']}")
        print(f"📋 内容预览:\n{readme_result['content']}")
        print(f"📁 分析的文件: {', '.join(readme_result['analyzed_files'])}")
    else:
        print("❌ README生成失败")

if __name__ == "__main__":
    asyncio.run(main())