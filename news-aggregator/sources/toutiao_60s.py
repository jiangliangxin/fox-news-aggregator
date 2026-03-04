"""
今日头条 - 60s API
https://60s.viki.moe/v2/toutiao
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Toutiao60sSource(BaseSource):
    """今日头条"""
    
    name = "今日头条"
    source_id = "60s_toutiao"
    category = "hot"
    group = "toutiao"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/toutiao"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            items.append(NewsItem(
                id=str(len(items)),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="头条",
                category=self.category,
            ))
        
        return items
