"""
Fox新闻聚合器 - 数据源自动注册

每个数据源一个文件，自动注册到全局注册表
"""

import os
import importlib
from pathlib import Path
from typing import Dict, List, Type, Optional
from dataclasses import dataclass, field

# ============================================================================
# 核心数据结构
# ============================================================================

@dataclass
class NewsItem:
    """统一新闻格式"""
    id: str
    title: str
    url: str = ""
    source: str = ""              # 来源名称
    category: str = "hot"         # hot/tech/finance/world
    hot_value: int = 0            # 热度值
    pub_date: int = 0             # 发布时间戳
    extra: dict = field(default_factory=dict)  # 扩展信息
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "hot_value": self.hot_value,
            "pub_date": self.pub_date,
            "extra": self.extra,
        }


# ============================================================================
# 数据源基类
# ============================================================================

class BaseSource:
    """数据源基类"""
    
    # 源信息（子类必须覆盖）
    name: str = ""                # 源名称（如"知乎热榜"）
    source_id: str = ""           # 源ID（如"zhihu"）
    category: str = "hot"         # 分类
    group: str = ""               # 分组（用于降级）
    priority: int = 0             # 优先级（0最高，数字越大优先级越低）
    enabled: bool = True          # 是否启用
    
    def fetch(self) -> List[NewsItem]:
        """获取新闻列表（子类必须实现）"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.enabled
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


# ============================================================================
# 全局注册表
# ============================================================================

# 数据源注册表 {source_id: SourceClass}
SOURCE_REGISTRY: Dict[str, Type[BaseSource]] = {}

# 分组映射 {group: [source_ids]}
GROUP_MAPPING: Dict[str, List[str]] = {}


def register_source(source_cls: Type[BaseSource]) -> Type[BaseSource]:
    """注册数据源（装饰器）"""
    if not source_cls.source_id:
        raise ValueError(f"Source {source_cls.__name__} must have source_id")
    
    SOURCE_REGISTRY[source_cls.source_id] = source_cls
    
    # 添加到分组
    group = source_cls.group or source_cls.source_id.split("_")[0]
    if group not in GROUP_MAPPING:
        GROUP_MAPPING[group] = []
    GROUP_MAPPING[group].append(source_cls.source_id)
    
    return source_cls


def get_source(source_id: str) -> Optional[BaseSource]:
    """获取数据源实例"""
    cls = SOURCE_REGISTRY.get(source_id)
    return cls() if cls else None


def get_sources_by_group(group: str) -> List[BaseSource]:
    """获取指定分组的所有源（按优先级排序）"""
    source_ids = GROUP_MAPPING.get(group, [])
    sources = [SOURCE_REGISTRY[sid]() for sid in source_ids if sid in SOURCE_REGISTRY]
    return sorted(sources, key=lambda s: s.priority)


def list_sources() -> Dict[str, List[str]]:
    """列出所有数据源"""
    return {
        group: [
            f"{sid} ({SOURCE_REGISTRY[sid].name})"
            for sid in sids if sid in SOURCE_REGISTRY
        ]
        for group, sids in GROUP_MAPPING.items()
    }


# ============================================================================
# 自动注册
# ============================================================================

def auto_register():
    """自动注册所有数据源"""
    sources_dir = Path(__file__).parent
    
    for file in sorted(sources_dir.glob("*.py")):
        if file.name.startswith("_") or file.name == "__init__.py":
            continue
        
        module_name = file.stem
        try:
            module = importlib.import_module(f".{module_name}", package=__package__ or "sources")
            # 模块导入时会自动执行 @register_source 装饰器
        except Exception as e:
            print(f"⚠️ 加载数据源 {module_name} 失败: {e}")


# 自动注册所有源
auto_register()
