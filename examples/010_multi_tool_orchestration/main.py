#!/usr/bin/env python3

import asyncio
import json
import os
import sys
sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations, WebClient

class DataAnalysisWorkflow:
    """
    数据分析工作流 - 协调多个工具完成复杂任务
    
    展示纯Python如何优雅地组合多个独立工具
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        self.web_client = WebClient()
    
    async def analyze_financial_data(self, data_sources: dict) -> dict:
        """
        多步骤金融数据分析工作流:
        1. 从多个来源收集数据
        2. 进行数学计算
        3. 生成分析报告
        4. 保存结果
        """
        
        print("💰 开始金融数据分析工作流...")
        workflow_results = {"steps": [], "final_report": None}
        
        # 步骤1: 收集数据
        print("📊 步骤1: 收集数据")
        collected_data = {}
        
        # 从文件读取历史数据
        if "file_path" in data_sources:
            file_result = await self.file_ops.read_file(data_sources["file_path"])
            if file_result["success"]:
                try:
                    collected_data["historical"] = json.loads(file_result["content"])
                    print(f"  ✅ 从文件读取了历史数据")
                except:
                    collected_data["historical"] = {"error": "文件格式错误"}
                    print(f"  ❌ 文件格式错误")
        
        # 从Web API获取实时数据(模拟)
        if "api_urls" in data_sources:
            web_data = {}
            for name, url in data_sources["api_urls"].items():
                web_result = await self.web_client.fetch(url)
                if web_result["success"]:
                    web_data[name] = web_result["content"][:500]  # 限制长度
                    print(f"  ✅ 获取了 {name} 数据")
            collected_data["realtime"] = web_data
        
        workflow_results["steps"].append({
            "name": "数据收集",
            "status": "完成",
            "data": list(collected_data.keys())
        })
        
        # 步骤2: 数学计算
        print("🧮 步骤2: 执行计算")
        calculations = {}
        
        # 示例计算
        calc_expressions = [
            "100 * 1.05**5",  # 复利计算
            "(200 + 300 + 150) / 3",  # 平均值
            "1000 * 0.08 * 2",  # 简单利息
        ]
        
        for i, expr in enumerate(calc_expressions):
            calc_result = self.calculator.calculate(expr)
            if calc_result["success"]:
                calculations[f"calculation_{i+1}"] = {
                    "expression": expr,
                    "result": calc_result["result"]
                }
                print(f"  ✅ 计算完成: {expr} = {calc_result['result']}")
        
        workflow_results["steps"].append({
            "name": "数学计算",
            "status": "完成", 
            "results": calculations
        })
        
        # 步骤3: LLM分析
        print("🤖 步骤3: 生成分析报告")
        
        analysis_data = {
            "collected_data": collected_data,
            "calculations": calculations,
            "metadata": {
                "data_sources": len(collected_data),
                "calculations_performed": len(calculations)
            }
        }
        
        analysis_prompt = f"""
基于以下财务数据和计算结果，生成一份专业的分析报告:

收集的数据:
{json.dumps(collected_data, indent=2, ensure_ascii=False)}

计算结果:
{json.dumps(calculations, indent=2, ensure_ascii=False)}

请提供:
1. 数据概览
2. 关键发现
3. 风险分析
4. 投资建议

保持专业但易于理解。
"""
        
        report_response = await self.llm.generate(analysis_prompt)
        final_report = report_response["content"]
        
        workflow_results["steps"].append({
            "name": "LLM分析",
            "status": "完成",
            "report_length": len(final_report)
        })
        
        # 步骤4: 保存结果
        print("💾 步骤4: 保存分析结果")
        
        report_data = {
            "timestamp": "2024-01-01T00:00:00Z",  # 实际应用中使用真实时间
            "workflow_results": workflow_results,
            "final_report": final_report,
            "raw_data": analysis_data
        }
        
        save_path = "financial_analysis_report.json"
        save_result = await self.file_ops.write_file(
            save_path, 
            json.dumps(report_data, indent=2, ensure_ascii=False)
        )
        
        if save_result["success"]:
            print(f"  ✅ 报告已保存到: {save_path}")
            workflow_results["steps"].append({
                "name": "保存结果",
                "status": "完成",
                "file_path": save_path
            })
        
        workflow_results["final_report"] = final_report
        return workflow_results

class ResearchPipeline:
    """
    研究管道 - 自动化研究工作流
    """
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        self.web_client = WebClient()
    
    async def conduct_research(self, topic: str) -> dict:
        """执行完整的研究流程"""
        
        print(f"🔬 开始研究主题: {topic}")
        
        # 1. 生成研究计划
        print("📋 生成研究计划...")
        plan_prompt = f"""
为主题 "{topic}" 制定一个研究计划。

请提供:
1. 3个关键研究问题
2. 需要查找的数据类型
3. 可能需要的计算
4. 预期的研究产出

格式化为JSON，方便程序处理。
"""
        
        plan_response = await self.llm.generate(plan_prompt)
        
        # 2. 执行信息搜索 (模拟)
        print("🔍 执行信息搜索...")
        search_results = {
            "academic_papers": "模拟学术论文摘要...",
            "industry_reports": "模拟行业报告数据...",
            "statistical_data": "模拟统计数据..."
        }
        
        # 3. 数据分析 (如果需要)
        print("📊 执行数据分析...")
        analysis_results = {}
        
        # 模拟一些相关计算
        if "计算" in topic or "数据" in topic or "统计" in topic:
            expressions = ["100 / 7", "2.5 * 3.14159", "sqrt(144)"]  # sqrt会失败，展示错误处理
            
            for expr in expressions:
                calc_result = self.calculator.calculate(expr)
                analysis_results[expr] = calc_result
        
        # 4. 生成最终报告
        print("📄 生成研究报告...")
        
        research_data = {
            "topic": topic,
            "plan": plan_response["content"],
            "search_results": search_results,
            "analysis": analysis_results
        }
        
        final_prompt = f"""
基于以下研究数据生成一份完整的研究报告:

{json.dumps(research_data, indent=2, ensure_ascii=False)}

报告应包含:
1. 执行摘要
2. 研究方法
3. 主要发现
4. 结论和建议

保持学术严谨性但易于理解。
"""
        
        final_response = await self.llm.generate(final_prompt)
        
        # 5. 保存研究报告
        report_filename = f"research_report_{topic.replace(' ', '_')}.md"
        await self.file_ops.write_file(report_filename, final_response["content"])
        
        return {
            "topic": topic,
            "plan": plan_response["content"],
            "report_file": report_filename,
            "report_preview": final_response["content"][:500] + "...",
            "data_analyzed": len(analysis_results),
            "sources_searched": len(search_results)
        }

async def main():
    """演示多工具协调的复杂工作流"""
    
    # 示例1: 金融数据分析工作流
    print("=== 示例1: 金融数据分析工作流 ===")
    
    # 创建示例数据文件
    sample_data = {
        "monthly_returns": [0.05, 0.03, -0.02, 0.07, 0.04],
        "portfolio_value": 100000,
        "risk_level": "moderate"
    }
    
    file_ops = FileOperations()
    await file_ops.write_file("sample_financial_data.json", json.dumps(sample_data))
    
    workflow = DataAnalysisWorkflow("openai")
    
    data_sources = {
        "file_path": "sample_financial_data.json",
        "api_urls": {
            "market_data": "https://api.example.com/market",  # 模拟URL
            "news_feed": "https://api.example.com/news"       # 模拟URL
        }
    }
    
    workflow_result = await workflow.analyze_financial_data(data_sources)
    
    print(f"📊 工作流完成!")
    print(f"执行步骤: {len(workflow_result['steps'])}")
    for step in workflow_result["steps"]:
        print(f"  - {step['name']}: {step['status']}")
    print(f"📄 最终报告: {workflow_result['final_report'][:200]}...")
    
    print("\n" + "="*60 + "\n")
    
    # 示例2: 研究管道
    print("=== 示例2: 自动化研究管道 ===")
    
    pipeline = ResearchPipeline("openai")
    research_result = await pipeline.conduct_research("人工智能在医疗领域的应用")
    
    print(f"🔬 研究完成!")
    print(f"主题: {research_result['topic']}")
    print(f"分析数据点: {research_result['data_analyzed']}")
    print(f"搜索来源: {research_result['sources_searched']}")
    print(f"报告文件: {research_result['report_file']}")
    print(f"📋 报告预览:\n{research_result['report_preview']}")

if __name__ == "__main__":
    asyncio.run(main())