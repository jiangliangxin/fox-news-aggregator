"""
B站热搜词
https://s.search.bilibili.com/main/hotword
"""

import requests
from urllib.parse import quote
from . import NewsItem, BaseSource, register_source


@register_source
class BilibiliHotwordSource(BaseSource):
    """B站热搜词"""
    
    name = "B站热搜"
    source_id = "bilibili_hotword"
    category = "hot"
    group = "bilibili"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://s.search.bilibili.com/main/hotword?limit=30"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("list", []):
            keyword = item.get("keyword", "")
            show_name = item.get("show_name", keyword)
            
            items.append(NewsItem(
                id=keyword,
                title=show_name,
                url=f"https://search.bilibili.com/all?keyword={quote(keyword)}",
                source="B站",
                category=self.category,
                extra={"icon": item.get("icon", "")},
            ))
        
        return items
