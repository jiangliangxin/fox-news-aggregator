# Fox新闻聚合器 - 架构设计文档

## 一、问题分析

### 当前问题
1. **重复代码**：resilient.py 和 newsnow_fetcher.py 都实现了相同的数据源
2. **职责混乱**：fetcher.py 既是聚合器又是获取器
3. **导入复杂**：需要手动导入每个模块
4. **难以扩展**：新增数据源需要修改多个文件

### 参考项目架构

**DailyHotApi (65+源)**
```
src/
├── routes/           # 每个源一个文件
│   ├── bilibili.ts
│   ├── zhihu.ts
│   ├── weibo.ts
│   └── ...
├── utils/            # 工具函数
└── types.ts          # 类型定义
```

**NewsNow (30+源)**
```
server/
├── sources/          # 每个源一个文件
│   ├── weibo.ts
│   ├── zhihu.ts
│   └── ...
├── utils/            # 工具函数
└── database/         # 数据存储
```

---

## 二、最佳实践设计

### 设计原则

1. **单一职责**：每个数据源一个文件
2. **统一接口**：所有源返回相同的 `NewsItem` 格式
3. **插件化**：新增源只需添加文件，自动注册
4. **弹性设计**：内置降级、重试、缓存
5. **可观测性**：健康状态、错误日志、统计信息

### 目标架构

```
news-aggregator/
├── sources/                    # 数据源（每个源一个文件）
│   ├── __init__.py            # 自动注册所有源
│   ├── base.py                # 基类和接口定义
│   ├── _60s_daily.py          # 60s每日精选
│   ├── _60s_weibo.py          # 60s微博热搜
│   ├── _60s_zhihu.py          # 60s知乎热榜
│   ├── zhihu_api.py           # 知乎官方API
│   ├── bilibili_hotword.py    # B站热搜词
│   ├── bilibili_popular.py    # B站热门视频
│   ├── douban_movie.py        # 豆瓣电影
│   ├── thepaper.py            # 澎湃新闻
│   ├── v2ex.py                # V2EX
│   ├── weibo_cookie.py        # 微博(需Cookie)
│   └── github_trending.py     # GitHub Trending
│
├── core/                       # 核心模块
│   ├── fetcher.py             # 统一获取器（带降级）
│   ├── cache.py               # 缓存管理
│   ├── health.py              # 健康检查
│   └── dedup.py               # 去重
│
├── analysis/                   # 分析引擎（已有）
│   ├── correlation.py
│   ├── alerts.py
│   └── entities.py
│
├── output/                     # 输出模块
│   ├── report.py              # 日报生成
│   └── json_export.py         # JSON导出
│
├── config/                     # 配置（保留）
│   └── settings.py
│
└── aggregator.py               # 主入口
```

---

## 三、核心接口设计

### 3.1 数据源接口

```python
# sources/base.py
from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod

@dataclass
class NewsItem:
    """统一新闻格式"""
    id: str
    title: str
    url: str
    source: str              # 来源名称
    category: str = "hot"    # hot/tech/finance/world
    hot_value: int = 0       # 热度值
    pub_date: int = 0        # 发布时间戳
    extra: dict = None       # 扩展信息

class BaseSource(ABC):
    """数据源基类"""
    
    # 源信息
    name: str = ""           # 源名称
    category: str = "hot"    # 分类
    priority: int = 0        # 优先级（用于降级）
    
    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """获取新闻列表"""
        pass
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True
```

### 3.2 数据源实现示例

```python
# sources/zhihu_api.py
from .base import BaseSource, NewsItem
import requests

class ZhihuAPISource(BaseSource):
    name = "知乎热榜"
    category = "hot"
    priority = 1  # 降级优先级
    
    def fetch(self) -> List[NewsItem]:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-list-web?limit=20"
        headers = {"User-Agent": "Mozilla/5.0..."}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        return [
            NewsItem(
                id=item["target"]["link"]["url"].split("/")[-1],
                title=item["target"]["title_area"]["text"],
                url=item["target"]["link"]["url"],
                source="知乎",
                hot_value=self._parse_hot(item.get("metrics_area", {}).get("text", "0"))
            )
            for item in data.get("data", [])
        ]

# 注册到全局
SOURCE_REGISTRY["zhihu_api"] = ZhihuAPISource
```

### 3.3 弹性获取器

```python
# core/fetcher.py
class ResilientFetcher:
    """弹性获取器 - 自动降级"""
    
    def __init__(self):
        self.health = HealthTracker()
        self.cache = CacheManager()
    
    def fetch_with_fallback(self, source_group: str) -> List[NewsItem]:
        """带降级的获取"""
        
        # 获取该组的所有源（按优先级排序）
        sources = get_sources_by_group(source_group)
        
        for source_cls in sources:
            source = source_cls()
            source_name = f"{source_group}:{source.name}"
            
            # 1. 检查缓存
            cached = self.cache.get(source_name)
            if cached:
                return cached
            
            # 2. 检查健康状态
            if not self.health.is_available(source_name):
                continue
            
            # 3. 尝试获取
            try:
                items = source.fetch()
                self.health.record_success(source_name)
                self.cache.set(source_name, items)
                return items
            except Exception as e:
                self.health.record_failure(source_name)
                continue
        
        return []  # 所有源都失败
```

### 3.4 自动注册机制

```python
# sources/__init__.py
import os
import importlib
from pathlib import Path

SOURCE_REGISTRY = {}

def auto_register():
    """自动注册所有数据源"""
    sources_dir = Path(__file__).parent
    
    for file in sources_dir.glob("*.py"):
        if file.name.startswith("_") or file.name == "__init__.py":
            continue
        
        module = importlib.import_module(f".{file.stem}", package="sources")
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseSource) and attr is not BaseSource:
                key = file.stem  # 使用文件名作为key
                SOURCE_REGISTRY[key] = attr

def get_sources_by_group(group: str) -> List[type]:
    """获取指定组的所有源（按优先级）"""
    sources = [
        cls for key, cls in SOURCE_REGISTRY.items()
        if key.startswith(group)
    ]
    return sorted(sources, key=lambda s: s.priority)

# 自动注册
auto_register()
```

---

## 四、数据源分组策略

### 分组定义

| 分组 | 主源（优先） | 降级源 | 说明 |
|------|-------------|--------|------|
| zhihu | _60s_zhihu | zhihu_api | 知乎热榜 |
| weibo | _60s_weibo | weibo_cookie | 微博热搜 |
| bilibili | bilibili_hotword | - | B站热搜 |
| daily | _60s_daily | - | 每日精选 |
| tech | ithome_rss | ithome_api | 科技资讯 |
| finance | bloomberg_rss | - | 财经新闻 |

### 降级规则

1. 主源连续3次失败 → 标记不健康
2. 不健康源进入5分钟冷却期
3. 冷却期内使用降级源
4. 降级源成功后自动恢复主源

---

## 五、迁移计划

### Phase 1: 创建新架构（不影响现有功能）
1. 创建 sources/base.py 定义接口
2. 创建 sources/ 目录结构
3. 逐个迁移现有数据源

### Phase 2: 实现弹性获取器
1. 创建 core/fetcher.py
2. 实现 health.py 健康检查
3. 整合现有 cache_manager.py

### Phase 3: 整合和测试
1. 修改 aggregator.py 使用新架构
2. 更新 generate_daily_news.py
3. 删除旧文件（newsnow_fetcher.py）

### Phase 4: 清理
1. 删除冗余代码
2. 更新文档
3. 添加测试

---

## 六、预期收益

1. **可维护性**：每个数据源一个文件，职责清晰
2. **可扩展性**：新增源只需添加文件，自动注册
3. **稳定性**：多级降级，自动恢复
4. **可观测性**：健康状态、错误日志
5. **代码量**：减少约30%重复代码

---

生成时间: 2026-02-26
