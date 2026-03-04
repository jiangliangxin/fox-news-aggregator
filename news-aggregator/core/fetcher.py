"""
弹性获取器

自动降级、重试、缓存的统一获取接口
"""

import time
from typing import List, Optional
from .health import health_tracker
from .cache import cache_manager


# 导入数据源注册表
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources import (
    NewsItem,
    SOURCE_REGISTRY,
    GROUP_MAPPING,
    get_source,
    get_sources_by_group,
)


class ResilientFetcher:
    """弹性获取器"""
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.health = health_tracker
        self.cache = cache_manager
    
    def fetch_source(self, source_id: str) -> List[NewsItem]:
        """获取单个数据源（带缓存）"""
        
        # 1. 检查缓存
        if self.use_cache:
            cache_key = f"source:{source_id}"
            cached = self.cache.get(cache_key)
            if cached:
                return [NewsItem(**item) if isinstance(item, dict) else item for item in cached]
        
        # 2. 检查健康状态
        if not self.health.is_available(source_id):
            return []
        
        # 3. 获取数据
        source = get_source(source_id)
        if not source:
            return []
        
        try:
            items = source.fetch()
            self.health.record_success(source_id)
            
            # 缓存结果
            if self.use_cache and items:
                self.cache.set(cache_key, [item.to_dict() for item in items])
            
            return items
        except Exception as e:
            self.health.record_failure(source_id)
            print(f"⚠️ 数据源 {source_id} 获取失败: {e}")
            return []
    
    def fetch_group(self, group: str, use_fallback: bool = True) -> List[NewsItem]:
        """
        获取数据源分组（带降级）
        
        Args:
            group: 分组名称
            use_fallback: 是否使用降级源
        
        Returns:
            新闻列表（第一个可用源的结果）
        """
        sources = get_sources_by_group(group)
        
        if not sources:
            print(f"⚠️ 分组 {group} 没有可用的数据源")
            return []
        
        for source in sources:
            source_id = source.source_id
            
            # 检查健康状态
            if not self.health.is_available(source_id):
                continue
            
            # 尝试获取
            items = self.fetch_source(source_id)
            
            if items:
                # 如果不是第一个源，说明发生了降级
                if source.priority > 0:
                    print(f"✅ 降级到 {source.name}")
                return items
        
        return []
    
    def fetch_all(self, groups: List[str] = None) -> dict:
        """
        获取所有数据
        
        Args:
            groups: 要获取的分组列表，None表示全部
        
        Returns:
            {group: [NewsItem]}
        """
        if groups is None:
            groups = list(GROUP_MAPPING.keys())
        
        result = {}
        for group in groups:
            items = self.fetch_group(group)
            if items:
                result[group] = items
        
        return result
    
    def get_health_report(self) -> str:
        """获取健康状态报告"""
        return self.health.get_report()


# 便捷函数
_fetcher: Optional[ResilientFetcher] = None


def get_fetcher(use_cache: bool = True) -> ResilientFetcher:
    """获取全局获取器"""
    global _fetcher
    if _fetcher is None:
        _fetcher = ResilientFetcher(use_cache=use_cache)
    return _fetcher


def fetch_source(source_id: str) -> List[NewsItem]:
    """获取单个数据源"""
    return get_fetcher().fetch_source(source_id)


def fetch_group(group: str) -> List[NewsItem]:
    """获取数据源分组"""
    return get_fetcher().fetch_group(group)
