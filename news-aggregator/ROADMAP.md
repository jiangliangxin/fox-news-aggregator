# Fox新闻聚合器 - 升级路线图

## 目标：融合 DailyHotApi + NewsNow 的优秀设计

---

## 一、数据源架构升级

### 1.1 统一数据源格式（学习DailyHotApi）

```python
# 所有源返回统一格式
class NewsItem:
    id: str           # 唯一标识
    title: str        # 标题
    url: str          # 原文链接
    source: str       # 来源名称
    category: str     # 分类 (hot/tech/finance/world)
    pub_date: int     # 发布时间戳
    extra: dict       # 扩展信息
        - hot_value: int   # 热度值
        - author: str      # 作者
        - summary: str     # 摘要
        - icon: str        # 图标/封面
```

### 1.2 源配置系统（学习NewsNow）

```python
# sources_config.py
SOURCES = {
    "weibo": {
        "name": "微博热搜",
        "color": "#ff8200",
        "home": "https://weibo.com",
        "column": "china",      # 分类列
        "type": "hottest",      # hottest/realtime
        "fetcher": "api",       # api/rss/crawler
        "cache_minutes": 30,
        "min_interval": 2,      # 最小抓取间隔（分钟）
    },
    "zhihu": {
        "name": "知乎热榜",
        ...
    }
}
```

---

## 二、智能爬取策略（NewsNow核心）

### 2.1 自适应抓取间隔

```python
class AdaptiveFetcher:
    """根据源的更新频率自动调整抓取间隔"""
    
    def __init__(self):
        self.source_stats = {}  # 记录每个源的更新频率
        
    def get_interval(self, source_id: str) -> int:
        """计算下次抓取间隔（分钟）"""
        stats = self.source_stats.get(source_id, {})
        
        # 基础间隔 = 配置的最小间隔
        base_interval = SOURCES[source_id].get("min_interval", 5)
        
        # 如果最近3次都没更新，增加间隔
        no_update_count = stats.get("no_update_count", 0)
        if no_update_count >= 3:
            return min(base_interval * 2, 60)  # 最多60分钟
        
        # 如果频繁更新，保持最小间隔
        return base_interval
```

### 2.2 智能缓存

```python
class SmartCache:
    """带过期策略的智能缓存"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str, max_age: int = 1800):
        """获取缓存，max_age默认30分钟"""
        if key not in self.cache:
            return None
        if time.time() - self.timestamps[key] > max_age:
            return None
        return self.cache[key]
```

---

## 三、爬虫模块（DailyHotApi）

### 3.1 Puppeteer爬虫（处理JS渲染）

```python
# 需要安装: pip install pyppeteer
import asyncio
from pyppeteer import launch

async def fetch_js_page(url: str) -> str:
    """使用无头浏览器抓取JS渲染页面"""
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    # 设置User-Agent避免被封
    await page.setUserAgent('Mozilla/5.0 ...')
    
    await page.goto(url, waitUntil='networkidle0')
    content = await page.content()
    
    await browser.close()
    return content
```

### 3.2 反爬策略

```python
class AntiScraping:
    """反爬虫策略"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
        ...
    ]
    
    @staticmethod
    def get_random_ua() -> str:
        return random.choice(AntiScraping.USER_AGENTS)
    
    @staticmethod
    async def fetch_with_retry(url: str, max_retries: int = 3):
        for i in range(max_retries):
            try:
                await asyncio.sleep(random.uniform(1, 3))  # 随机延迟
                return await fetch(url)
            except Exception as e:
                if i == max_retries - 1:
                    raise
```

---

## 四、新增数据源

### 4.1 从DailyHotApi借鉴的源

- [x] 微博热搜 (已有)
- [x] 知乎热榜 (已有)
- [x] 抖音热点 (已有)
- [ ] B站热门
- [ ] 百度贴吧
- [ ] 豆瓣电影
- [ ] 虎嗅24小时
- [ ] 澎湃新闻
- [ ] V2EX
- [ ] 掘金热榜
- [ ] 吾爱破解
- [ ] 地震速报
- [ ] 气象预警

### 4.2 财经专用源（主人炒股需求）

- [ ] 东方财富
- [ ] 同花顺
- [ ] 雪球热门
- [ ] 第一财经
- [ ] 财新网
- [ ] 证券时报

---

## 五、实现优先级

### Phase 1 (本周)
1. 统一数据源格式
2. 添加智能缓存
3. 新增B站、虎嗅、澎湃源

### Phase 2 (下周)
1. 自适应抓取策略
2. Puppeteer爬虫模块
3. 新增财经专用源

### Phase 3 (后续)
1. RSS输出支持
2. MCP Server集成
3. Web界面（可选）

---

## 六、文件结构

```
news-aggregator/
├── config/
│   ├── sources.py          # 数据源配置
│   └── settings.py         # 全局设置
├── fetchers/
│   ├── base.py             # 基础fetcher
│   ├── api_fetcher.py      # API调用
│   ├── rss_fetcher.py      # RSS解析
│   └── crawler_fetcher.py  # 爬虫抓取
├── cache/
│   └── smart_cache.py      # 智能缓存
├── analysis/
│   ├── correlation.py      # 关联分析
│   ├── alerts.py           # 告警检测
│   └── entities.py         # 实体识别
└── output/
    ├── json_output.py      # JSON输出
    └── rss_output.py       # RSS输出
```

---

生成时间: 2026-02-26
