"""
微博热搜 - 60s API
https://60s.viki.moe/v2/weibo
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Weibo60sSource(BaseSource):
    """微博热搜"""
    
    name = "微博热搜"
    source_id = "60s_weibo"
    category = "hot"
    group = "weibo"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/weibo"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            items.append(NewsItem(
                id=item.get("url", "").split("/")[-1] or str(len(items)),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="微博",
                category=self.category,
                hot_value=item.get("hot_value", 0),
            ))
        
        return items
