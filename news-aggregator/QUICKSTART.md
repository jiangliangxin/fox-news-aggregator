# Fox新闻聚合器 v3.0

插件化新闻聚合系统，支持39个数据源。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 生成日报
python3 generate_daily_news.py

# 运行测试
pytest tests/ -v
```

## 架构

```
news-aggregator/
├── sources/          # 13个数据源（每个源一个文件）
├── core/             # 核心模块（fetcher, cache, health）
├── analysis/         # 分析引擎
├── tests/            # 测试文件
├── config/           # 配置文件
└── requirements.txt  # 依赖
```

## 数据源

- API数据源: 12个
- RSS数据源: 27个
- 总计: 39个活跃数据源

## 文档

- [README.md](README.md) - 使用指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [ROADMAP.md](ROADMAP.md) - 升级路线图
