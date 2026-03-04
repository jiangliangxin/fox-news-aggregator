"""
AI 专业数据源配置

包含 OpenAI、Anthropic、arXiv、Hugging Face 等 AI 领域高质量源
"""

# ==================== AI 专业数据源 ====================
AI_RSS_SOURCES = {
    "ai_models": {
        "name": "AI大模型",
        "category": "ai",
        "feeds": [
            # OpenAI 官方博客
            "https://openai.com/blog/rss.xml",
            # Anthropic 博客
            "https://www.anthropic.com/news/rss",
            # Google DeepMind 博客  
            "https://deepmind.google/discover/blog/rss.xml",
            # Meta AI 博客
            "https://ai.meta.com/blog/rss.xml",
        ]
    },
    
    "ai_opensource": {
        "name": "AI开源生态",
        "category": "ai",
        "feeds": [
            # Hugging Face 博客
            "https://huggingface.co/blog/feed.xml",
            # LangChain 博客
            "https://blog.langchain.dev/rss/",
            # Ollama 博客
            "https://ollama.com/blog/rss.xml",
        ]
    },
    
    "ai_research": {
        "name": "AI前沿论文",
        "category": "ai",
        "feeds": [
            # arXiv CS.CL (NLP)
            "http://export.arxiv.org/api/query?search_query=cat:cs.CL&max_results=15&sortBy=submittedDate",
            # arXiv CS.LG (机器学习)
            "http://export.arxiv.org/api/query?search_query=cat:cs.LG&max_results=15&sortBy=submittedDate",
            # Papers With Code
            "https://paperswithcode.com/rss",
        ]
    },
    
    "ai_tools": {
        "name": "AI开发工具",
        "category": "ai",
        "feeds": [
            # GitHub Copilot
            "https://github.blog/tag/copilot/feed/",
            # Vercel AI
            "https://vercel.com/blog/topics/ai.rss",
        ]
    },
    
    "ai_news": {
        "name": "AI行业动态",
        "category": "ai",
        "feeds": [
            # VentureBeat AI
            "https://venturebeat.com/category/ai/feed/",
            # MIT Technology Review AI
            "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        ]
    },
}
