"""
Fox新闻聚合器测试
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources import SOURCE_REGISTRY, get_source, get_sources_by_group


class TestSources:
    """测试数据源"""
    
    def test_source_registry_not_empty(self):
        """测试数据源注册表不为空"""
        assert len(SOURCE_REGISTRY) > 0, "数据源注册表为空"
    
    def test_all_sources_have_required_fields(self):
        """测试所有数据源都有必需字段"""
        for source_id, source_cls in SOURCE_REGISTRY.items():
            source = source_cls()
            assert source.name, f"{source_id} 缺少 name"
            assert source.source_id, f"{source_id} 缺少 source_id"
            assert source.category, f"{source_id} 缺少 category"
    
    def test_zhihu_api_fetch(self):
        """测试知乎API数据源"""
        source = get_source('zhihu_api')
        assert source is not None, "知乎API数据源不存在"
        
        items = source.fetch()
        assert isinstance(items, list), "fetch()应该返回列表"
        if items:
            assert hasattr(items[0], 'title'), "NewsItem应该有title属性"
    
    def test_bilibili_hotword_fetch(self):
        """测试B站热搜数据源"""
        source = get_source('bilibili_hotword')
        assert source is not None, "B站热搜数据源不存在"
        
        items = source.fetch()
        assert isinstance(items, list), "fetch()应该返回列表"
    
    def test_group_has_sources(self):
        """测试分组有数据源"""
        sources = get_sources_by_group('zhihu')
        assert len(sources) > 0, "知乎分组应该有数据源"


class TestCache:
    """测试缓存"""
    
    def test_cache_directory_exists(self):
        """测试缓存目录存在"""
        cache_dir = Path(__file__).parent.parent / ".cache"
        assert cache_dir.exists(), "缓存目录不存在"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
