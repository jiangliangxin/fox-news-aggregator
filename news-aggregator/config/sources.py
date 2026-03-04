"""
RSS数据源配置

包含27个RSS数据源
"""

# ==================== 国际科技 ====================
RSS_SOURCES = {
    "tech_intl": {
        "name": "国际科技",
        "category": "tech",
        "feeds": [
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.wired.com/feed/rss",
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://rss.slashdot.org/Slashdot/slashdotMain",
            "https://techcrunch.com/tag/artificial-intelligence/feed/",
            "https://www.wired.com/feed/tag/ai/latest/rss",
            "https://hnrss.org/frontpage",
            "https://www.reddit.com/r/technology/.rss",
            "https://www.reddit.com/r/artificial/.rss",
            "https://www.reddit.com/r/MachineLearning/.rss",
            "https://www.reddit.com/r/OpenAI/.rss",
        ]
    },
    
    "tech_cn": {
        "name": "中文科技",
        "category": "tech",
        "feeds": [
            "https://36kr.com/feed",
            "https://www.ithome.com/rss/",
            "https://sspai.com/feed",
            "https://www.infoq.cn/feed",
        ]
    },
    
    "finance": {
        "name": "财经",
        "category": "finance",
        "feeds": [
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.ft.com/rss/home",
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "https://feeds.marketwatch.com/marketwatch/topstories",
            "https://wallstreetcn.com/news/global",
        ]
    },
    
    "science": {
        "name": "科学文化",
        "category": "science",
        "feeds": [
            "https://api.quantamagazine.org/feed/",
            "https://www.symmetrymagazine.org/feed",
            "https://aeon.co/feed",
            "https://nautil.us/feed/all",
        ]
    },
}

# ==================== 扩展RSS源 ====================
EXTENDED_RSS_SOURCES = {
    "intl_intel": {
        "name": "国际情报",
        "category": "world",
        "feeds": [
            "https://www.csis.org/rss.xml",
            "https://www.brookings.edu/feed/",
            "https://www.cfr.org/feed.xml",
            "https://www.rand.org/blog.xml",
            "https://breakingdefense.com/feed/",
            "https://warontherocks.com/feed/",
        ]
    },
}
