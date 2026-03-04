"""
抖音热点 - 60s API
https://60s.viki.moe/v2/douyin
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Douyin60sSource(BaseSource):
    """抖音热点"""
    
    name = "抖音热点"
    source_id = "60s_douyin"
    category = "hot"
    group = "douyin"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/douyin"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            items.append(NewsItem(
                id=str(len(items)),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="抖音",
                category=self.category,
                hot_value=item.get("hot_value", 0),
            ))
        
        return items
