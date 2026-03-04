"""
知乎热榜 - 60s API
https://60s.viki.moe/v2/zhihu
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class Zhihu60sSource(BaseSource):
    """知乎热榜（60s API）"""
    
    name = "知乎热榜"
    source_id = "60s_zhihu"
    category = "hot"
    group = "zhihu"
    priority = 0  # 主源
    
    def fetch(self) -> list:
        url = "https://60s.viki.moe/v2/zhihu"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            items.append(NewsItem(
                id=item.get("url", "").split("/")[-1] or str(len(items)),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="知乎",
                category=self.category,
                hot_value=item.get("hot_value", 0),
            ))
        
        return items
