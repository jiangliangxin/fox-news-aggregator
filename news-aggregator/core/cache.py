"""
缓存管理模块

基于文件的缓存系统，支持过期时间
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    timestamp: float
    ttl: int  # 过期时间（秒）
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 1800):
        """
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒），默认30分钟
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        
        # 内存缓存
        self.memory_cache: dict = {}
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 先查内存缓存
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self.memory_cache[key]
        
        # 再查文件缓存
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                
                entry = CacheEntry(
                    data=data["data"],
                    timestamp=data["timestamp"],
                    ttl=data["ttl"],
                )
                
                if not entry.is_expired():
                    # 加载到内存
                    self.memory_cache[key] = entry
                    return entry.data
                else:
                    # 删除过期缓存
                    cache_path.unlink()
            except:
                pass
        
        return None
    
    def set(self, key: str, data: Any, ttl: int = None):
        """设置缓存"""
        ttl = ttl or self.default_ttl
        timestamp = time.time()
        
        # 内存缓存
        self.memory_cache[key] = CacheEntry(
            data=data,
            timestamp=timestamp,
            ttl=ttl,
        )
        
        # 文件缓存
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "key": key,
                    "data": data,
                    "timestamp": timestamp,
                    "ttl": ttl,
                }, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear_expired(self):
        """清理过期缓存"""
        # 清理内存缓存
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v.is_expired()
        ]
        for k in expired_keys:
            del self.memory_cache[k]
        
        # 清理文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                
                entry = CacheEntry(
                    data=data["data"],
                    timestamp=data["timestamp"],
                    ttl=data["ttl"],
                )
                
                if entry.is_expired():
                    cache_file.unlink()
            except:
                pass
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        memory_count = len(self.memory_cache)
        file_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            "memory_entries": memory_count,
            "file_entries": file_count,
            "cache_dir": str(self.cache_dir),
        }


# 全局缓存管理器
cache_manager = CacheManager(
    cache_dir=Path(__file__).parent.parent / ".cache",
    default_ttl=1800,  # 30分钟
)
