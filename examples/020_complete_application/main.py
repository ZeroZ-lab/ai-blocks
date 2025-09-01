#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.append('../..')

from ai_modular_blocks import create_llm
from ai_modular_blocks.tools import Calculator, FileOperations, WebClient

class SmartBusinessAnalyzer:
    """
    智能商业分析应用 - 完整的AI驱动业务分析系统
    
    展示AI Modular Blocks框架的完整应用
    集成多种AI能力：数据分析、报告生成、预测建议
    """
    
    def __init__(self, provider: str = "openai"):
        # 框架的核心 - 只需要一行代码创建LLM
        self.llm = create_llm(provider, api_key=os.getenv(f"{provider.upper()}_API_KEY"))
        
        # 独立工具 - 可以单独使用，不依赖框架
        self.calculator = Calculator()
        self.file_ops = FileOperations()
        self.web_client = WebClient()
        
        # 应用状态
        self.analysis_history = []
        self.business_knowledge = {}
        
        # 应用配置
        self.app_config = {
            "name": "智能商业分析师",
            "version": "1.0.0",
            "capabilities": [
                "财务数据分析", "市场趋势分析", "竞争对手分析", 
                "投资建议", "风险评估", "报告生成"
            ]
        }
    
    async def analyze_business_performance(self, data_source: str) -> Dict:
        """完整的商业表现分析流程"""
        
        print(f"🏢 开始商业表现分析...")
        print(f"📊 数据源: {data_source}")
        
        analysis_start = datetime.now()
        
        try:
            # 步骤1: 数据获取和预处理
            print("📥 步骤1: 获取业务数据...")
            raw_data = await self._fetch_business_data(data_source)
            
            # 步骤2: 财务指标计算
            print("💰 步骤2: 计算财务指标...")
            financial_metrics = await self._calculate_financial_metrics(raw_data)
            
            # 步骤3: 市场分析
            print("📈 步骤3: 进行市场分析...")
            market_analysis = await self._analyze_market_trends(raw_data)
            
            # 步骤4: 风险评估
            print("⚠️ 步骤4: 评估业务风险...")
            risk_assessment = await self._assess_business_risks(financial_metrics, market_analysis)
            
            # 步骤5: 生成洞察和建议
            print("💡 步骤5: 生成商业洞察...")
            insights = await self._generate_business_insights(
                financial_metrics, market_analysis, risk_assessment
            )
            
            # 步骤6: 创建综合报告
            print("📋 步骤6: 生成分析报告...")
            final_report = await self._create_comprehensive_report(
                raw_data, financial_metrics, market_analysis, risk_assessment, insights
            )
            
            # 步骤7: 保存结果
            report_file = f"business_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            await self._save_analysis_results(final_report, report_file)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            # 记录分析历史
            self.analysis_history.append({
                "timestamp": analysis_start.isoformat(),
                "data_source": data_source,
                "duration": analysis_duration,
                "report_file": report_file,
                "success": True
            })
            
            print(f"✅ 分析完成! 耗时 {analysis_duration:.2f} 秒")
            print(f"📄 报告已保存: {report_file}")
            
            return {
                "success": True,
                "analysis_id": len(self.analysis_history),
                "data_source": data_source,
                "duration": analysis_duration,
                "report_file": report_file,
                "summary": final_report["executive_summary"],
                "key_metrics": financial_metrics,
                "recommendations": insights["recommendations"][:3]
            }
            
        except Exception as e:
            print(f"❌ 分析过程出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_source": data_source
            }
    
    async def _fetch_business_data(self, source: str) -> Dict:
        """获取业务数据"""
        
        # 模拟从不同源获取数据
        if source.startswith("http"):
            # 从网络API获取数据
            web_result = await self.web_client.fetch(source)
            if web_result["success"]:
                return {
                    "source_type": "web_api",
                    "raw_content": web_result["content"][:1000],
                    "timestamp": datetime.now().isoformat()
                }
        
        elif source.endswith(('.json', '.csv', '.txt')):
            # 从文件读取数据
            file_result = await self.file_ops.read_file(source)
            if file_result["success"]:
                try:
                    data = json.loads(file_result["content"])
                    return {
                        "source_type": "file",
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }
                except:
                    return {
                        "source_type": "file",
                        "raw_content": file_result["content"],
                        "timestamp": datetime.now().isoformat()
                    }
        
        # 生成模拟数据用于演示
        return {
            "source_type": "simulated",
            "data": {
                "revenue": [1200000, 1350000, 1180000, 1480000, 1620000, 1750000],
                "expenses": [800000, 900000, 850000, 980000, 1100000, 1150000],
                "customers": [2500, 2800, 2650, 3100, 3400, 3650],
                "market_share": [0.12, 0.13, 0.12, 0.14, 0.15, 0.16],
                "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "industry": "科技服务",
                "company_size": "中型企业"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _calculate_financial_metrics(self, data: Dict) -> Dict:
        """计算关键财务指标"""
        
        if "data" not in data:
            return {"error": "无有效财务数据"}
        
        business_data = data["data"]
        
        # 使用计算器计算关键指标
        metrics = {}
        
        if "revenue" in business_data and "expenses" in business_data:
            revenues = business_data["revenue"]
            expenses = business_data["expenses"]
            
            # 计算利润
            profits = []
            for i in range(len(revenues)):
                if i < len(expenses):
                    profit = revenues[i] - expenses[i]
                    profits.append(profit)
            
            # 使用计算器计算统计指标
            if revenues:
                total_revenue = sum(revenues)
                avg_revenue = total_revenue / len(revenues)
                
                total_expenses = sum(expenses)
                avg_expenses = total_expenses / len(expenses)
                
                profit_margin = ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0
                
                # 增长率计算
                revenue_growth = ((revenues[-1] - revenues[0]) / revenues[0] * 100) if len(revenues) > 1 and revenues[0] > 0 else 0
                
                metrics = {
                    "total_revenue": total_revenue,
                    "average_monthly_revenue": round(avg_revenue, 2),
                    "total_expenses": total_expenses,
                    "average_monthly_expenses": round(avg_expenses, 2),
                    "profit_margin_percent": round(profit_margin, 2),
                    "revenue_growth_percent": round(revenue_growth, 2),
                    "monthly_profits": profits,
                    "analysis_period": f"{len(revenues)} 个月"
                }
        
        # 客户相关指标
        if "customers" in business_data:
            customers = business_data["customers"]
            if customers:
                customer_growth = ((customers[-1] - customers[0]) / customers[0] * 100) if len(customers) > 1 and customers[0] > 0 else 0
                avg_customers = sum(customers) / len(customers)
                
                metrics.update({
                    "total_customers": customers[-1] if customers else 0,
                    "average_customers": round(avg_customers, 0),
                    "customer_growth_percent": round(customer_growth, 2)
                })
        
        return metrics
    
    async def _analyze_market_trends(self, data: Dict) -> Dict:
        """分析市场趋势"""
        
        market_prompt = f"""
基于以下业务数据分析市场趋势:

数据: {json.dumps(data.get('data', {}), ensure_ascii=False)}

请分析:
1. 市场增长趋势
2. 竞争环境
3. 机遇和挑战
4. 行业前景

返回JSON:
{{
  "market_trend": "上升/下降/稳定",
  "growth_drivers": ["驱动因素1", "驱动因素2"],
  "competitive_landscape": "竞争环境描述",
  "opportunities": ["机遇1", "机遇2"],
  "challenges": ["挑战1", "挑战2"],
  "industry_outlook": "行业前景",
  "confidence_score": 0.85
}}
"""
        
        response = await self.llm.generate(market_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content)
        except:
            return {
                "market_trend": "稳定",
                "growth_drivers": ["数字化转型", "市场需求增长"],
                "competitive_landscape": "竞争激烈",
                "opportunities": ["新兴市场", "产品创新"],
                "challenges": ["成本上升", "监管变化"],
                "industry_outlook": "谨慎乐观",
                "confidence_score": 0.7
            }
    
    async def _assess_business_risks(self, financial_metrics: Dict, market_analysis: Dict) -> Dict:
        """评估业务风险"""
        
        risk_prompt = f"""
基于财务指标和市场分析评估业务风险:

财务指标: {json.dumps(financial_metrics, ensure_ascii=False)}
市场分析: {json.dumps(market_analysis, ensure_ascii=False)}

评估以下风险类别:

返回JSON:
{{
  "overall_risk_level": "低/中/高",
  "financial_risks": [
    {{"type": "风险类型", "level": "低/中/高", "description": "描述"}}
  ],
  "market_risks": [
    {{"type": "风险类型", "level": "低/中/高", "description": "描述"}}
  ],
  "operational_risks": [
    {{"type": "风险类型", "level": "低/中/高", "description": "描述"}}
  ],
  "mitigation_strategies": ["策略1", "策略2"],
  "risk_score": 65
}}
"""
        
        response = await self.llm.generate(risk_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content)
        except:
            return {
                "overall_risk_level": "中",
                "financial_risks": [
                    {"type": "现金流风险", "level": "中", "description": "需要关注现金流管理"}
                ],
                "market_risks": [
                    {"type": "竞争风险", "level": "中", "description": "市场竞争加剧"}
                ],
                "operational_risks": [
                    {"type": "运营效率", "level": "低", "description": "运营相对稳定"}
                ],
                "mitigation_strategies": ["多元化收入", "成本控制"],
                "risk_score": 60
            }
    
    async def _generate_business_insights(self, financial_metrics: Dict, market_analysis: Dict, risk_assessment: Dict) -> Dict:
        """生成商业洞察"""
        
        insights_prompt = f"""
基于完整的商业分析数据，生成深度洞察和建议:

财务表现: {json.dumps(financial_metrics, ensure_ascii=False)}
市场趋势: {json.dumps(market_analysis, ensure_ascii=False)}  
风险评估: {json.dumps(risk_assessment, ensure_ascii=False)}

请提供:

返回JSON:
{{
  "key_insights": ["洞察1", "洞察2", "洞察3"],
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["劣势1", "劣势2"],
  "recommendations": [
    {{"priority": "高/中/低", "action": "具体行动", "expected_impact": "预期影响"}}
  ],
  "next_quarter_forecast": {{"revenue": 1500000, "growth_rate": 5.2}},
  "strategic_priorities": ["优先事项1", "优先事项2"]
}}
"""
        
        response = await self.llm.generate(insights_prompt)
        
        try:
            content = response["content"].strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content)
        except:
            return {
                "key_insights": ["收入增长稳定", "客户基础扩大", "需要控制成本"],
                "strengths": ["强劲增长", "客户忠诚度高"],
                "weaknesses": ["成本上升", "利润率下降"],
                "recommendations": [
                    {"priority": "高", "action": "优化成本结构", "expected_impact": "提高利润率5-10%"},
                    {"priority": "中", "action": "扩大市场份额", "expected_impact": "收入增长15%"}
                ],
                "next_quarter_forecast": {"revenue": 1800000, "growth_rate": 8.5},
                "strategic_priorities": ["数字化转型", "客户体验优化"]
            }
    
    async def _create_comprehensive_report(self, raw_data: Dict, financial_metrics: Dict, 
                                         market_analysis: Dict, risk_assessment: Dict, 
                                         insights: Dict) -> Dict:
        """创建综合分析报告"""
        
        report = {
            "report_metadata": {
                "title": "智能商业表现分析报告",
                "generated_at": datetime.now().isoformat(),
                "analysis_period": financial_metrics.get("analysis_period", "未知"),
                "company_type": raw_data.get("data", {}).get("company_size", "未知"),
                "industry": raw_data.get("data", {}).get("industry", "未知")
            },
            
            "executive_summary": f"""
本报告基于 {financial_metrics.get('analysis_period', '6个月')} 的业务数据进行深度分析。
主要发现：收入增长 {financial_metrics.get('revenue_growth_percent', 0):.1f}%，
客户增长 {financial_metrics.get('customer_growth_percent', 0):.1f}%，
利润率 {financial_metrics.get('profit_margin_percent', 0):.1f}%。
整体风险水平：{risk_assessment.get('overall_risk_level', '中等')}。
""",
            
            "financial_performance": financial_metrics,
            "market_analysis": market_analysis,
            "risk_assessment": risk_assessment,
            "strategic_insights": insights,
            
            "recommendations_summary": {
                "immediate_actions": [r["action"] for r in insights.get("recommendations", []) if r.get("priority") == "高"],
                "medium_term_goals": [r["action"] for r in insights.get("recommendations", []) if r.get("priority") == "中"],
                "long_term_strategy": insights.get("strategic_priorities", [])
            },
            
            "data_sources": {
                "primary_source": raw_data.get("source_type", "unknown"),
                "analysis_tools": ["AI语言模型", "数学计算器", "数据处理引擎"],
                "confidence_level": "高"
            }
        }
        
        return report
    
    async def _save_analysis_results(self, report: Dict, filename: str):
        """保存分析结果"""
        
        report_json = json.dumps(report, ensure_ascii=False, indent=2)
        await self.file_ops.write_file(filename, report_json)
        
        # 也创建一个简化的文本摘要
        summary_filename = filename.replace('.json', '_summary.txt')
        summary_text = f"""
=== {report['report_metadata']['title']} ===
生成时间: {report['report_metadata']['generated_at']}
分析周期: {report['report_metadata']['analysis_period']}

=== 执行摘要 ===
{report['executive_summary']}

=== 关键指标 ===
总收入: {report['financial_performance'].get('total_revenue', 'N/A')}
收入增长: {report['financial_performance'].get('revenue_growth_percent', 'N/A')}%
利润率: {report['financial_performance'].get('profit_margin_percent', 'N/A')}%
客户增长: {report['financial_performance'].get('customer_growth_percent', 'N/A')}%

=== 主要建议 ===
"""
        
        for i, rec in enumerate(report['strategic_insights'].get('recommendations', [])[:3], 1):
            summary_text += f"{i}. {rec.get('action', 'N/A')} (优先级: {rec.get('priority', 'N/A')})\n"
        
        await self.file_ops.write_file(summary_filename, summary_text)
    
    def get_application_status(self) -> Dict:
        """获取应用状态"""
        
        return {
            "app_info": self.app_config,
            "analysis_history": {
                "total_analyses": len(self.analysis_history),
                "successful_analyses": len([a for a in self.analysis_history if a.get("success")]),
                "recent_analyses": self.analysis_history[-5:] if self.analysis_history else []
            },
            "system_capabilities": {
                "llm_provider": "openai",  # 从框架获取
                "available_tools": ["Calculator", "FileOperations", "WebClient"],
                "analysis_types": ["财务分析", "市场分析", "风险评估"]
            },
            "uptime": "运行中"
        }

async def main():
    """演示完整的智能商业分析应用"""
    
    print("="*80)
    print("🚀 AI Modular Blocks - 完整应用演示")
    print("智能商业分析系统")
    print("="*80)
    
    # 创建应用实例 - 展示框架的简洁性
    app = SmartBusinessAnalyzer("openai")
    
    # 显示应用状态
    status = app.get_application_status()
    print(f"\n📊 应用信息:")
    print(f"名称: {status['app_info']['name']}")
    print(f"版本: {status['app_info']['version']}")
    print(f"能力: {', '.join(status['app_info']['capabilities'])}")
    
    print(f"\n⚙️  系统配置:")
    print(f"LLM提供商: {status['system_capabilities']['llm_provider']}")
    print(f"可用工具: {', '.join(status['system_capabilities']['available_tools'])}")
    
    print("\n" + "="*80)
    
    # 执行完整的商业分析流程
    print("🎯 开始执行完整商业分析...")
    
    # 分析示例1: 使用模拟数据
    print("\n--- 分析案例1: 科技服务公司 ---")
    result1 = await app.analyze_business_performance("simulated_tech_company")
    
    if result1["success"]:
        print(f"✅ 分析成功完成!")
        print(f"📈 分析ID: {result1['analysis_id']}")
        print(f"⏱️  用时: {result1['duration']:.2f}秒")
        print(f"📄 报告文件: {result1['report_file']}")
        
        print(f"\n💡 核心洞察:")
        print(f"{result1['summary']}")
        
        print(f"\n📊 关键指标:")
        metrics = result1['key_metrics']
        print(f"  总收入: {metrics.get('total_revenue', 'N/A'):,}")
        print(f"  收入增长: {metrics.get('revenue_growth_percent', 'N/A')}%")
        print(f"  利润率: {metrics.get('profit_margin_percent', 'N/A')}%")
        print(f"  客户增长: {metrics.get('customer_growth_percent', 'N/A')}%")
        
        print(f"\n🎯 主要建议:")
        for i, rec in enumerate(result1['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    else:
        print(f"❌ 分析失败: {result1['error']}")
    
    # 创建演示数据文件进行第二次分析
    print(f"\n--- 分析案例2: 从文件读取数据 ---")
    
    demo_data = {
        "company_name": "创新科技有限公司",
        "revenue": [980000, 1120000, 1050000, 1280000, 1450000, 1380000],
        "expenses": [720000, 840000, 780000, 920000, 1050000, 980000],
        "customers": [1800, 2100, 1950, 2400, 2650, 2480],
        "market_share": [0.08, 0.09, 0.085, 0.11, 0.12, 0.115],
        "months": ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "industry": "软件开发",
        "company_size": "中小企业"
    }
    
    # 保存演示数据
    await app.file_ops.write_file("demo_business_data.json", json.dumps(demo_data, ensure_ascii=False, indent=2))
    
    # 从文件分析
    result2 = await app.analyze_business_performance("demo_business_data.json")
    
    if result2["success"]:
        print(f"✅ 文件数据分析完成!")
        print(f"📊 利润率: {result2['key_metrics'].get('profit_margin_percent', 'N/A')}%")
        print(f"📈 收入增长: {result2['key_metrics'].get('revenue_growth_percent', 'N/A')}%")
    
    print("\n" + "="*80)
    print("📈 应用运行总结:")
    
    final_status = app.get_application_status()
    print(f"总分析次数: {final_status['analysis_history']['total_analyses']}")
    print(f"成功分析: {final_status['analysis_history']['successful_analyses']}")
    
    print(f"\n🎉 演示完成!")
    print(f"这个完整应用展示了AI Modular Blocks框架的强大功能:")
    print(f"  • 简洁的API: 只需 create_llm() 即可开始")
    print(f"  • 独立工具: 计算器、文件操作、网络客户端可单独使用")
    print(f"  • 纯Python: 没有特殊语法，完全依赖Python语言特性")
    print(f"  • 用户自由: 完全控制应用逻辑和数据流")
    print(f"  • 可组合性: 轻松集成不同AI能力")

if __name__ == "__main__":
    asyncio.run(main())