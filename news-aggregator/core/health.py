"""
健康检查模块

追踪数据源的健康状态，实现熔断机制
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SourceHealth:
    """数据源健康状态"""
    name: str
    last_success: float = 0
    last_failure: float = 0
    failure_count: int = 0
    success_count: int = 0
    is_healthy: bool = True
    
    # 配置
    max_failures: int = 3        # 连续失败次数阈值
    cooldown_seconds: int = 300  # 冷却期（秒）
    
    def record_success(self):
        """记录成功"""
        self.last_success = time.time()
        self.failure_count = 0
        self.success_count += 1
        self.is_healthy = True
    
    def record_failure(self):
        """记录失败"""
        self.last_failure = time.time()
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            self.is_healthy = False
    
    def should_retry(self) -> bool:
        """判断是否应该重试"""
        if self.is_healthy:
            return True
        # 不健康时，冷却期后才重试
        return time.time() - self.last_failure > self.cooldown_seconds
    
    def time_since_last_failure(self) -> float:
        """距离上次失败的秒数"""
        if self.last_failure == 0:
            return float('inf')
        return time.time() - self.last_failure
    
    def reset(self):
        """重置状态"""
        self.failure_count = 0
        self.is_healthy = True


class HealthTracker:
    """健康状态追踪器"""
    
    def __init__(self):
        self.sources: Dict[str, SourceHealth] = {}
    
    def get(self, source_id: str) -> SourceHealth:
        """获取数据源健康状态"""
        if source_id not in self.sources:
            self.sources[source_id] = SourceHealth(name=source_id)
        return self.sources[source_id]
    
    def is_available(self, source_id: str) -> bool:
        """检查数据源是否可用"""
        return self.get(source_id).should_retry()
    
    def record_success(self, source_id: str):
        """记录成功"""
        self.get(source_id).record_success()
    
    def record_failure(self, source_id: str):
        """记录失败"""
        self.get(source_id).record_failure()
    
    def reset(self, source_id: str):
        """重置数据源状态"""
        self.get(source_id).reset()
    
    def get_report(self) -> str:
        """获取健康状态报告"""
        lines = ["📊 数据源健康状态报告", ""]
        
        healthy = []
        unhealthy = []
        
        for source_id, health in self.sources.items():
            if health.is_healthy:
                healthy.append(source_id)
            else:
                cooldown_left = max(0, health.cooldown_seconds - health.time_since_last_failure())
                unhealthy.append(f"  ❌ {source_id}: 冷却中（{int(cooldown_left)}秒）")
        
        if healthy:
            lines.append("✅ 健康:")
            for s in healthy:
                lines.append(f"  {s}")
        
        if unhealthy:
            lines.append("")
            lines.append("❌ 不健康:")
            lines.extend(unhealthy)
        
        return "\n".join(lines)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        healthy = sum(1 for h in self.sources.values() if h.is_healthy)
        total = len(self.sources)
        
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "sources": {
                sid: {
                    "is_healthy": h.is_healthy,
                    "failure_count": h.failure_count,
                    "success_count": h.success_count,
                }
                for sid, h in self.sources.items()
            }
        }


# 全局健康追踪器
health_tracker = HealthTracker()
