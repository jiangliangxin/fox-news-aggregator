"""
B站热门视频
https://api.bilibili.com/x/web-interface/popular
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class BilibiliPopularSource(BaseSource):
    """B站热门视频"""
    
    name = "B站热门"
    source_id = "bilibili_popular"
    category = "hot"
    group = "bilibili"
    priority = 1
    
    def fetch(self) -> list:
        url = "https://api.bilibili.com/x/web-interface/popular?ps=20"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for video in data.get("data", {}).get("list", []):
            stat = video.get("stat", {})
            owner = video.get("owner", {})
            
            items.append(NewsItem(
                id=video.get("bvid", ""),
                title=video.get("title", ""),
                url=f"https://www.bilibili.com/video/{video.get('bvid', '')}",
                source="B站",
                category=self.category,
                hot_value=stat.get("view", 0),
                extra={
                    "author": owner.get("name", ""),
                    "view": stat.get("view", 0),
                    "like": stat.get("like", 0),
                    "pic": video.get("pic", ""),
                },
            ))
        
        return items
