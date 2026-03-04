"""
豆瓣热门电影
https://m.douban.com/rexxar/api/v2/subject/recent_hot/movie
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class DoubanMovieSource(BaseSource):
    """豆瓣热门电影"""
    
    name = "豆瓣电影"
    source_id = "douban_movie"
    category = "entertainment"
    group = "douban"
    priority = 0
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://movie.douban.com/",
        "Accept": "application/json",
    }
    
    def fetch(self) -> list:
        url = "https://m.douban.com/rexxar/api/v2/subject/recent_hot/movie"
        
        resp = requests.get(url, headers=self.HEADERS, timeout=10)
        data = resp.json()
        
        items = []
        for movie in data.get("items", []):
            rating = movie.get("rating", {})
            
            items.append(NewsItem(
                id=movie.get("id", ""),
                title=movie.get("title", ""),
                url=f"https://movie.douban.com/subject/{movie.get('id', '')}",
                source="豆瓣",
                category=self.category,
                extra={
                    "rating": rating.get("value", 0),
                    "count": rating.get("count", 0),
                    "card_subtitle": movie.get("card_subtitle", ""),
                    "pic": movie.get("pic", {}).get("large", ""),
                },
            ))
        
        return items
