# Fox新闻聚合器 v3.0

基于 DailyHotApi 和 NewsNow 最佳实践的插件化新闻聚合系统。

## 架构

```
news-aggregator/
├── sources/              # 数据源（每个源一个文件）
│   ├── __init__.py      # 基类 + 自动注册
│   ├── daily_60s.py     # 每天60秒
│   ├── weibo_60s.py     # 微博热搜
│   ├── zhihu_60s.py     # 知乎（60s）
│   ├── zhihu_api.py     # 知乎（官方API降级）
│   ├── douyin_60s.py    # 抖音热点
│   ├── toutiao_60s.py   # 今日头条
│   ├── epic_60s.py      # Epic免费游戏
│   ├── bilibili_hotword.py  # B站热搜
│   ├── bilibili_popular.py  # B站热门
│   ├── douban.py        # 豆瓣电影
│   ├── thepaper.py      # 澎湃新闻
│   └── v2ex.py          # V2EX
│
├── core/                 # 核心模块
│   ├── fetcher.py       # 弹性获取器（自动降级）
│   ├── health.py        # 健康检查（熔断机制）
│   └── cache.py         # 缓存管理（30分钟过期）
│
├── analysis/             # 分析引擎
│   ├── correlation.py   # 关联分析（跨源追踪）
│   ├── alerts.py        # 告警检测（敏感话题）
│   └── entities.py      # 实体识别（人物/机构）
│
└── config/               # 配置文件
    ├── sources.py       # RSS数据源配置
    └── extended_sources.py
```

## 特性

- **插件化架构**：新增数据源只需创建文件，自动注册
- **弹性获取**：主源失败自动降级（60s API → 官方API）
- **健康追踪**：连续3次失败熔断，5分钟冷却期
- **智能缓存**：30分钟过期，内存+文件双层缓存
- **关联分析**：跨源追踪热门话题，识别市场热点

## 快速开始

```python
from core.fetcher import fetch_source, fetch_group

# 获取单个数据源
items = fetch_source('zhihu_api')
print(f"获取 {len(items)} 条知乎热榜")

# 获取分组（带降级）
items = fetch_group('zhihu')  # 60s优先，失败降级到api
print(f"获取 {len(items)} 条")
```

## 新增数据源

1. 创建 `sources/xxx.py`：

```python
from . import NewsItem, BaseSource, register_source

@register_source
class XxxSource(BaseSource):
    name = "XXX热榜"
    source_id = "xxx"
    category = "hot"
    group = "xxx"
    priority = 0  # 0最高，用于降级
    
    def fetch(self) -> list:
        # 实现获取逻辑
        return [NewsItem(...)]
```

2. 自动注册，无需修改其他文件！

## 数据源分组

| 分组 | 主源 | 降级源 | 说明 |
|------|------|--------|------|
| zhihu | 60s_zhihu | zhihu_api | 知乎热榜 |
| weibo | 60s_weibo | - | 微博热搜 |
| bilibili | bilibili_hotword | bilibili_popular | B站 |
| daily | 60s_daily | - | 每日精选 |
| douban | douban_movie | - | 豆瓣电影 |
| v2ex | v2ex | - | V2EX |
| thepaper | thepaper | - | 澎湃新闻 |

## 生成日报

```bash
python3 generate_daily_news.py
```

输出：`daily_news_report.txt`

## 文件统计

- 数据源：12个文件（12个源）
- 核心模块：3个文件
- 分析模块：3个文件
- 总计：18个Python文件

## 参考

- [DailyHotApi](https://github.com/imsyy/DailyHotApi) - 65+数据源
- [NewsNow](https://github.com/ourongxing/newsnow) - 自适应爬取
