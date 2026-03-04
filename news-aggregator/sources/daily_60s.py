"""
每天60秒读懂世界
https://60s.viki.moe/v2/60s
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Daily60sSource(BaseSource):
    """每天60秒读懂世界"""
    
    name = "60秒读懂世界"
    source_id = "60s_daily"
    category = "hot"
    group = "daily"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/60s"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for i, news in enumerate(data.get("data", {}).get("news", [])):
            items.append(NewsItem(
                id=f"60s_{i}",
                title=news,
                source="60s",
                category=self.category,
            ))
        
        return items
