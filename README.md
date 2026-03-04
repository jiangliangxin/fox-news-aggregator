# 🦊 Fox News Aggregator

> 智能新闻聚合器 - 跨源关联分析 + 个性化推荐

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jiangliangxin/fox-news-aggregator)
[![GitHub stars](https://img.shields.io/github/stars/jiangliangxin/fox-news-aggregator.svg?](https://github.com/jiangliangxin/fox-news-aggregator/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/jiangliangxin/fox-news-aggregator.svg)](https://github.com/jiangliangxin/fox-news-aggregator/issues)

## ✨ 特性

### 核心功能
- 🔥 **跨源关联分析** - 识别发酵话题、跨源热点
- 🚨 **智能告警检测** - 自动识别战争、制裁、爆炸等重要事件
- 👤 **实体追踪** - 追踪热门人物、组织、国家
- 📊 **历史对比** - 对比昨日数据，显示新兴/退热话题
- 💰 **个性化推荐** - 根据投资组合匹配相关新闻（Phase 2）

### 技术架构
- 📦 **插件化数据源** - 每个源一个文件，自动注册
- 🛡️ **弹性获取器** - 自动降级、重试、熔断
- 💾 **智能缓存** - 减少重复请求，提升性能
- 📡 **健康监控** - 追踪数据源状态，自动切换备用源

### 数据源（39个活跃源）
- **API 源**（12个）：微博、知乎、B站、抖音、头条、豆瓣、V2EX、澎湃、Epic、60秒读懂世界
- **RSS 源**（27个）：TechCrunch、Wired、Bloomberg、FT、arXiv、Hacker News等

## 📋 开发路线图

### ✅ Phase 1: 激活分析引擎（已完成 - 2026-03-04）
- [x] 智能摘要头部（发酵话题、跨源热点、告警、人物）
- [x] 历史对比功能（对比昨日数据）
- [x] 修复分析引擎 bug（数据格式转换）
- [x] 替换生产环境（v4.0 上线）

### 🔄 Phase 2: 个性化推荐（计划中 - 下周）
**目标**：根据投资组合匹配相关新闻

**任务**：
- [ ] 创建投资组合配置（`config/portfolio.py`）
- [ ] 实现投资匹配分析（`analysis/portfolio_matcher.py`）
- [ ] 集成到日报系统
- [ ] 添加投资影响标注（高/中/低）

**示例输出**：
```
【投资相关】
🔴 美联储释放降息信号 → 纳指ETF、黄金ETF（高影响）
🟡 中芯国际获得新订单 → 科创ETF（中影响）
⚪ 阿里巴巴股价上涨 → 恒科ETF（低影响）
```

### 🔧 Phase 3: 减少外部依赖（计划中 - 下周）
**目标**：降低 60s API 依赖度从 78% 到 50%

**任务**：
- [ ] 新增财经数据源（雪球、东方财富、同花顺）
- [ ] 提升官方 API 优先级
- [ ] 新增备用源配置
- [ ] 实现自动降级机制

### 🚀 Phase 4: 智能摘要+实时告警（后续）
**目标**：输出精简 + 实时推送

**任务**：
- [ ] AI 智能摘要（100 字精华版）
- [ ] 实时告警推送（critical/high 级别立即推送）
- [ ] 日报精简版（50 条推送，465 条完整版保存文件）
- [ ] Web 界面改进（搜索、过滤）
- [ ] RSS 输出支持
- [ ] MCP Server 集成

## 🛠️ 技术债务

### 代码重构
- [ ] 统一 NewsItem 数据格式
- [ ] 删除重复的 60s 源文件，合并为通用 fetcher
- [ ] 添加单元测试（pytest）
- [ ] 创建全局配置（`config/settings.py`）

### 性能优化
- [ ] 异步抓取（asyncio）
- [ ] 代理池支持
- [ ] 增量更新机制

### 文档完善
- [ ] API 文档
- [ ] 部署文档
- [ ] 贡献指南

## 📊 性能指标

| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| 首次运行时间 | 50-60s | 30-40s |
| 缓存运行时间 | 15-20s | 10-15s |
| 数据源数量 | 39个 | 50+ |
| 60s API 依赖度 | 78% | 50% |
| 新闻总数 | 465+ | 500+ |

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/jiangliangxin/fox-news-aggregator.git
cd fox-news-aggregator

# 安装依赖
cd news-aggregator
pip install -r requirements.txt

# 运行日报生成
python3 generate_daily_news.py

# 查看输出
cat daily_news_report.txt
```

## 📝 配置

### 投资组合（个性化推荐）
编辑 `news-aggregator/config/portfolio.py`：
```python
PORTFOLIO = {
    "黄金ETF": {
        "code": "518880",
        "keywords": ["美元", "通胀", "CPI", "美联储", "地缘", "避险"],
        "impact": "high"
    },
    "纳指ETF": {
        "code": "513100",
        "keywords": ["美联储", "降息", "科技股", "AI", "纳指"],
        "impact": "high"
    }
}
```

### 数据源优先级
编辑 `news-aggregator/core/fetcher.py` 中的 `FALLBACK_CHAINS`

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)（待创建）

### 贡献方向
- 新增数据源
- 优化分析算法
- 改进文档
- 修复 bug
- 性能优化

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- **维护者**: Fox (OpenClaw AI Assistant)
- **项目主页**: https://github.com/jiangliangxin/fox-news-aggregator
- **问题反馈**: https://github.com/jiangliangxin/fox-news-aggregator/issues

---

**🦊 由 Fox v4.0 自动生成 | 2026-03-04**
