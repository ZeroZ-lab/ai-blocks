#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from typing import Dict, List, Any, Union

sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations, WebClient

class MultiModalAgent:
    """
    多模态代理 - 处理文本、数据、网页等多种输入
    
    纯Python实现，展示如何优雅地处理不同类型的任务
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        self.web_client = WebClient()
        
        # 模态处理器
        self.processors = {
            "text": self._process_text,
            "calculation": self._process_calculation,
            "file": self._process_file,
            "web": self._process_web,
            "data": self._process_data
        }
    
    async def understand_input(self, user_input: str, context: Dict = None) -> Dict:
        """理解输入的类型和意图"""
        
        analysis_prompt = f"""
分析以下用户输入的类型和处理方式:

输入: {user_input}
上下文: {json.dumps(context or {}, ensure_ascii=False)}

请判断这个输入需要什么类型的处理:

返回JSON:
{{
  "primary_type": "text|calculation|file|web|data",
  "secondary_types": ["other_type1", "other_type2"],
  "intent": "具体意图描述",
  "required_tools": ["tool1", "tool2"],
  "processing_strategy": "处理策略"
}}
"""
        
        response = await self.llm.generate(analysis_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content)
        except:
            return {
                "primary_type": "text",
                "secondary_types": [],
                "intent": "通用文本处理",
                "required_tools": ["llm"],
                "processing_strategy": "语言模型分析"
            }
    
    async def process_multi_modal_input(self, user_input: str, context: Dict = None) -> Dict:
        """处理多模态输入"""
        
        print(f"🔍 分析输入: {user_input}")
        
        # 1. 理解输入类型
        understanding = await self.understand_input(user_input, context)
        print(f"📊 识别类型: {understanding['primary_type']}")
        print(f"🎯 处理意图: {understanding['intent']}")
        
        # 2. 执行主要处理
        primary_result = await self.processors[understanding["primary_type"]](
            user_input, understanding
        )
        
        # 3. 执行辅助处理
        secondary_results = []
        for sec_type in understanding.get("secondary_types", []):
            if sec_type in self.processors and sec_type != understanding["primary_type"]:
                sec_result = await self.processors[sec_type](user_input, understanding)
                secondary_results.append({
                    "type": sec_type,
                    "result": sec_result
                })
        
        # 4. 综合结果
        final_result = await self._synthesize_results(
            user_input, primary_result, secondary_results, understanding
        )
        
        return {
            "input": user_input,
            "understanding": understanding,
            "primary_result": primary_result,
            "secondary_results": secondary_results,
            "final_answer": final_result
        }
    
    async def _process_text(self, input_text: str, understanding: Dict) -> Dict:
        """处理纯文本输入"""
        
        text_prompt = f"""
请处理以下文本请求:

输入: {input_text}
意图: {understanding['intent']}

提供有用的回答或分析。
"""
        
        response = await self.llm.generate(text_prompt)
        
        return {
            "type": "text_processing",
            "result": response["content"],
            "method": "LLM分析"
        }
    
    async def _process_calculation(self, input_text: str, understanding: Dict) -> Dict:
        """处理数学计算"""
        
        # 提取数学表达式
        extract_prompt = f"""
从以下文本中提取数学表达式:

输入: {input_text}

返回一个可以直接计算的表达式，例如: 2+3*4
如果没有明确的数学计算，返回: NONE
"""
        
        response = await self.llm.generate(extract_prompt)
        expression = response["content"].strip()
        
        if expression != "NONE" and expression:
            calc_result = self.calculator.calculate(expression)
            
            return {
                "type": "calculation",
                "expression": expression,
                "result": calc_result,
                "method": "数学计算器"
            }
        
        return {
            "type": "calculation",
            "result": {"success": False, "error": "未找到数学表达式"},
            "method": "计算器"
        }
    
    async def _process_file(self, input_text: str, understanding: Dict) -> Dict:
        """处理文件操作"""
        
        # 简化的文件操作处理
        if "读取" in input_text or "read" in input_text.lower():
            # 提取文件路径的简单逻辑
            words = input_text.split()
            potential_files = [w for w in words if '.' in w and '/' not in w[:3]]
            
            if potential_files:
                file_path = potential_files[0]
                read_result = await self.file_ops.read_file(file_path)
                
                return {
                    "type": "file_operation",
                    "operation": "read",
                    "file_path": file_path,
                    "result": read_result,
                    "method": "文件读取"
                }
        
        return {
            "type": "file_operation",
            "result": {"success": False, "error": "无法确定文件操作"},
            "method": "文件操作"
        }
    
    async def _process_web(self, input_text: str, understanding: Dict) -> Dict:
        """处理网页相关请求"""
        
        # 提取URL的简单逻辑
        import re
        urls = re.findall(r'https?://[^\s]+', input_text)
        
        if urls:
            url = urls[0]
            web_result = await self.web_client.fetch(url)
            
            return {
                "type": "web_processing",
                "url": url,
                "result": web_result,
                "method": "网页获取"
            }
        
        return {
            "type": "web_processing",
            "result": {"success": False, "error": "未找到有效URL"},
            "method": "网页处理"
        }
    
    async def _process_data(self, input_text: str, understanding: Dict) -> Dict:
        """处理数据分析请求"""
        
        data_prompt = f"""
分析以下数据相关请求:

输入: {input_text}

请提供数据分析的建议或执行步骤。
"""
        
        response = await self.llm.generate(data_prompt)
        
        return {
            "type": "data_analysis",
            "result": response["content"],
            "method": "数据分析"
        }
    
    async def _synthesize_results(
        self, 
        input_text: str, 
        primary_result: Dict, 
        secondary_results: List[Dict], 
        understanding: Dict
    ) -> str:
        """综合所有结果生成最终回答"""
        
        synthesis_prompt = f"""
用户输入: {input_text}
识别意图: {understanding['intent']}

主要处理结果:
{json.dumps(primary_result, ensure_ascii=False, indent=2)}

辅助处理结果:
{json.dumps(secondary_results, ensure_ascii=False, indent=2)}

请基于以上所有信息，为用户提供一个完整、有用的回答。
"""
        
        response = await self.llm.generate(synthesis_prompt)
        
        return response["content"]

# 专门的多模态应用实例
class PersonalAssistant:
    """个人助手 - 多模态代理的应用实例"""
    
    def __init__(self, provider: str = "openai"):
        self.agent = MultiModalAgent(provider)
        self.session_context = {}
    
    async def handle_request(self, user_input: str) -> Dict:
        """处理用户请求"""
        
        result = await self.agent.process_multi_modal_input(
            user_input, 
            self.session_context
        )
        
        # 更新会话上下文
        self.session_context["last_input"] = user_input
        self.session_context["last_result"] = result["final_answer"]
        
        return result
    
    async def analyze_document(self, file_path: str, question: str) -> Dict:
        """分析文档并回答问题"""
        
        combined_input = f"请分析文件 {file_path} 并回答: {question}"
        return await self.handle_request(combined_input)
    
    async def calculate_with_context(self, calculation: str, context: str) -> Dict:
        """在特定上下文中进行计算"""
        
        combined_input = f"在 {context} 的背景下，请计算: {calculation}"
        return await self.handle_request(combined_input)

async def main():
    """演示多模态代理"""
    
    print("=== 多模态代理演示 ===")
    
    assistant = PersonalAssistant("openai")
    
    # 测试不同类型的输入
    test_cases = [
        "计算 25 * 4 + 10 的结果",
        "请帮我分析一下人工智能的发展趋势",
        "如果我有10万元投资，年收益率6%，5年后会有多少钱？",
        "请读取文件 config.txt 的内容",
    ]
    
    print("测试多种类型的输入处理...\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"--- 测试 {i} ---")
        
        result = await assistant.handle_request(test_input)
        
        print(f"📥 输入: {result['input']}")
        print(f"🧠 理解: {result['understanding']['primary_type']} - {result['understanding']['intent']}")
        print(f"📤 回答: {result['final_answer'][:200]}...")
        
        if result['secondary_results']:
            print(f"🔧 辅助处理: {len(result['secondary_results'])} 个")
        
        print()
    
    print("="*60)
    print("🎯 多模态处理演示完成！")
    print("代理能够自动识别不同类型的输入并选择合适的处理方式。")

if __name__ == "__main__":
    asyncio.run(main())