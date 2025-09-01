"""
005 - 提示模板使用示例

展示用户自定义的提示模板系统：
- 纯Python字符串模板，无特殊DSL
- 用户可以自由定义模板格式和变量
- 支持动态模板和条件逻辑
"""

import asyncio
import os
from typing import Dict, Any, List
from string import Template
from dotenv import load_dotenv

from ai_modular_blocks import create_llm

load_dotenv()


class PromptTemplate:
    """用户自定义的提示模板类 - 使用Python标准模板"""
    
    def __init__(self, template: str, name: str = ""):
        self.template = Template(template)
        self.name = name
        self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """提取模板中的变量"""
        # 简单的变量提取（Python Template用$variable格式）
        import re
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        variables = re.findall(pattern, self.template.template)
        return list(set(variables))
    
    def render(self, **kwargs) -> str:
        """渲染模板"""
        try:
            return self.template.substitute(kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"模板变量 '{missing_var}' 未提供值")
    
    def safe_render(self, **kwargs) -> str:
        """安全渲染（未提供的变量保持原样）"""
        return self.template.safe_substitute(kwargs)
    
    def get_required_variables(self) -> List[str]:
        """获取必需的变量列表"""
        return self.variables.copy()


class PromptTemplateManager:
    """用户自定义的模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        
        # 代码审查模板
        self.register_template(
            "code_review",
            """作为一个资深的代码审查专家，请仔细审查以下$language代码：

代码内容：
```$language
$code
```

请从以下方面进行评估：
1. 代码质量和可读性
2. 性能优化建议
3. 潜在的安全问题
4. 最佳实践建议

审查重点：$focus

请提供具体的改进建议。"""
        )
        
        # 学习计划模板
        self.register_template(
            "learning_plan",
            """请为我制定一个关于$topic的学习计划。

我的背景：
- 当前水平：$current_level
- 可投入时间：每周$hours_per_week小时
- 学习目标：$goal
- 偏好的学习方式：$learning_style

请提供：
1. 详细的学习路径（分阶段）
2. 推荐的学习资源
3. 实践项目建议
4. 学习进度检查点

计划时长：$duration"""
        )
        
        # 产品分析模板
        self.register_template(
            "product_analysis",
            """请分析以下产品：

产品名称：$product_name
产品类型：$product_type
目标市场：$target_market

分析要求：
$analysis_requirements

请从以下角度进行分析：
1. 市场定位和竞争优势
2. 用户体验和功能特点
3. 商业模式和盈利能力
4. 发展趋势和改进建议

特别关注：$focus_areas"""
        )
        
        # 创意写作模板
        self.register_template(
            "creative_writing",
            """请创作一个$genre类型的$format。

主题：$theme
风格：$style
长度：约$length字

要求：
- 情节：$plot_requirements
- 角色：$character_requirements
- 背景设定：$setting
- 特殊要求：$special_requirements

请确保内容富有创意且引人入胜。"""
        )
    
    def register_template(self, name: str, template: str):
        """注册新模板"""
        self.templates[name] = PromptTemplate(template, name)
    
    def get_template(self, name: str) -> PromptTemplate:
        """获取模板"""
        if name not in self.templates:
            raise ValueError(f"未找到模板: {name}")
        return self.templates[name]
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
    
    def render_template(self, name: str, **kwargs) -> str:
        """渲染指定模板"""
        template = self.get_template(name)
        return template.render(**kwargs)


class TemplatedChatBot:
    """基于模板的聊天机器人"""
    
    def __init__(self, provider: str = "openai"):
        self.llm = create_llm(
            provider,
            api_key=os.getenv(f"{provider.upper()}_API_KEY"),
            temperature=0.7
        )
        self.template_manager = PromptTemplateManager()
        self.provider = provider
    
    async def chat_with_template(self, template_name: str, **variables) -> str:
        """使用模板进行对话"""
        try:
            # 渲染模板
            prompt = self.template_manager.render_template(template_name, **variables)
            
            print(f"📝 使用模板: {template_name}")
            print(f"🎯 生成的提示词预览:")
            print("-" * 40)
            # 显示前200字符
            preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
            print(preview)
            print("-" * 40)
            
            # 调用LLM
            response = await self.llm.generate(prompt)
            return response["content"]
            
        except Exception as e:
            return f"❌ 模板处理失败: {str(e)}"
    
    def show_template_info(self, template_name: str):
        """显示模板信息"""
        try:
            template = self.template_manager.get_template(template_name)
            print(f"\n📋 模板信息: {template_name}")
            print(f"必需变量: {', '.join(template.get_required_variables())}")
        except ValueError as e:
            print(f"❌ {e}")


async def demo_prompt_templates():
    """演示提示模板功能"""
    print("🚀 提示模板使用演示")
    print("=" * 50)
    
    # 创建聊天机器人
    providers = ["openai", "deepseek", "anthropic"]
    bot = None
    
    for provider in providers:
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        if api_key:
            try:
                bot = TemplatedChatBot(provider)
                print(f"✅ 使用 {provider.title()} 提供商")
                break
            except Exception as e:
                print(f"⚠️  {provider} 初始化失败: {e}")
    
    if not bot:
        print("❌ 没有可用的API密钥")
        return
    
    print(f"\n📚 可用模板: {', '.join(bot.template_manager.list_templates())}")
    
    # 演示1: 代码审查
    print(f"\n{'=' * 60}")
    print("📋 演示1: 代码审查模板")
    bot.show_template_info("code_review")
    
    sample_code = '''def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)'''
    
    response = await bot.chat_with_template(
        "code_review",
        language="Python",
        code=sample_code,
        focus="性能优化和算法改进"
    )
    
    print(f"\n🤖 AI回复:")
    print(response[:300] + "..." if len(response) > 300 else response)
    
    # 演示2: 学习计划
    print(f"\n{'=' * 60}")  
    print("📋 演示2: 学习计划模板")
    bot.show_template_info("learning_plan")
    
    response = await bot.chat_with_template(
        "learning_plan",
        topic="机器学习",
        current_level="编程基础，了解Python",
        hours_per_week="10",
        goal="能够独立完成机器学习项目",
        learning_style="理论结合实践",
        duration="3个月"
    )
    
    print(f"\n🤖 AI回复:")
    print(response[:400] + "..." if len(response) > 400 else response)
    
    print(f"\n{'=' * 60}")
    print("✅ 模板演示完成！")


async def interactive_template_mode():
    """交互式模板模式"""
    print("\n🎮 进入交互式模板模式")
    print("可用命令:")
    print("  - list: 列出所有模板")
    print("  - info <template_name>: 查看模板信息") 
    print("  - use <template_name>: 使用模板")
    print("  - quit: 退出")
    print("-" * 40)
    
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "deepseek"
    try:
        bot = TemplatedChatBot(provider)
        print(f"✅ 使用 {provider.title()}")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    while True:
        try:
            command = input("\n💻 命令: ").strip()
            
            if command == "quit":
                break
            elif command == "list":
                templates = bot.template_manager.list_templates()
                print(f"📚 可用模板: {', '.join(templates)}")
            elif command.startswith("info "):
                template_name = command[5:].strip()
                bot.show_template_info(template_name)
            elif command.startswith("use "):
                template_name = command[4:].strip()
                
                try:
                    template = bot.template_manager.get_template(template_name)
                    variables = {}
                    
                    print(f"\n📝 配置模板变量:")
                    for var in template.get_required_variables():
                        value = input(f"  {var}: ").strip()
                        if value:
                            variables[var] = value
                    
                    response = await bot.chat_with_template(template_name, **variables)
                    print(f"\n🤖 AI回复:")
                    print(response)
                    
                except Exception as e:
                    print(f"❌ 模板使用失败: {e}")
            elif command:
                print("❓ 未知命令，请输入 'list', 'info', 'use', 或 'quit'")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 命令执行异常: {e}")
    
    print("\n👋 退出交互模式！")


async def main():
    """主函数"""
    print("🌟 AI Modular Blocks - 提示模板示例")
    print("展示用户自定义的模板系统")
    print()
    
    # 演示模式
    await demo_prompt_templates()
    
    # 询问是否进入交互模式
    print(f"\n🎮 是否进入交互模式？(y/N)")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes']:
            await interactive_template_mode()
    except KeyboardInterrupt:
        pass
    
    print("\n🎯 核心优势:")
    print("- 使用Python标准Template，无需学习特殊语法")
    print("- 用户完全控制模板格式和变量规则")
    print("- 支持动态模板和复杂逻辑")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")