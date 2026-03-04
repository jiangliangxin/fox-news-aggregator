"""
澎湃新闻热榜
https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class ThePaperSource(BaseSource):
    """澎湃新闻热榜"""
    
    name = "澎湃新闻"
    source_id = "thepaper"
    category = "news"
    group = "thepaper"
    priority = 0
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    
    def fetch(self) -> list:
        url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
        headers = {"User-Agent": self.USER_AGENT}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for news in data.get("data", {}).get("hotNews", []):
            cont_id = news.get("contId", "")
            
            items.append(NewsItem(
                id=cont_id,
                title=news.get("name", ""),
                url=f"https://www.thepaper.cn/newsDetail_forward_{cont_id}",
                source="澎湃",
                category=self.category,
                extra={
                    "pub_time": news.get("pubTimeLong", ""),
                    "mobile_url": f"https://m.thepaper.cn/newsDetail_forward_{cont_id}",
                },
            ))
        
        return items
