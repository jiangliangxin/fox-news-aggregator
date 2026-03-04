"""
Epic免费游戏 - 60s API
https://60s.viki.moe/v2/epic
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Epic60sSource(BaseSource):
    """Epic免费游戏"""
    
    name = "Epic免费游戏"
    source_id = "60s_epic"
    category = "game"
    group = "epic"
    priority = 0
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/epic"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            items.append(NewsItem(
                id=item.get("code", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="Epic",
                category=self.category,
                extra={
                    "original_price": item.get("original_price_desc", ""),
                    "start_date": item.get("start_date", ""),
                    "end_date": item.get("end_date", ""),
                },
            ))
        
        return items
