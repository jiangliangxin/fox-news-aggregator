# 贡献指南

感谢你对 Fox News Aggregator 的关注！欢迎任何形式的贡献。

## 🎯 贡献方向

### 1. 新增数据源
在 `news-aggregator/sources/` 目录下创建新文件：

```python
# 示例：xueqiu.py（雪球热文）
from sources import BaseSource, NewsItem, register_source

@register_source
class XueqiuSource(BaseSource):
    name = "雪球热文"
    source_id = "xueqiu"
    category = "finance"
    group = "xueqiu"
    
    def fetch(self) -> List[NewsItem]:
        # 实现抓取逻辑
        pass
```

### 2. 优化分析算法
- 改进关联分析（`analysis/correlation.py`）
- 优化告警检测（`analysis/alerts.py`）
- 增强实体追踪（`analysis/entities.py`）

### 3. 改进文档
- 修复错别字
- 完善安装指南
- 添加使用案例

### 4. 修复 Bug
在 [Issues](https://github.com/jiangliangxin/fox-news-aggregator/issues) 中报告 bug

### 5. 性能优化
- 异步抓取
- 缓存策略
- 代理池支持

## 📝 提交规范

### Commit Message 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）**：
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- refactor: 代码重构
- perf: 性能优化
- test: 测试相关
- chore: 构建/工具

**示例**：
```
feat(sources): 新增雪球热文数据源

- 添加 xueqiu.py 数据源
- 实现热文抓取逻辑
- 添加单元测试

Closes #123
```

## 🔧 开发环境设置

```bash
# 1. Fork 仓库到你的账号

# 2. 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/fox-news-aggregator.git
cd fox-news-aggregator

# 3. 创建开发分支
git checkout -b feature/your-feature-name

# 4. 安装依赖
cd news-aggregator
pip install -r requirements.txt
pip install pytest  # 测试依赖

# 5. 运行测试
pytest tests/

# 6. 提交更改
git add .
git commit -m "feat: your feature description"

# 7. 推送到你的 fork
git push origin feature/your-feature-name

# 8. 创建 Pull Request
```

## ✅ 代码规范

### Python
- 遵循 PEP 8
- 使用类型注解（Type Hints）
- 添加文档字符串（Docstrings）
- 单元测试覆盖新功能

### 示例
```python
def fetch_news(source_id: str) -> List[NewsItem]:
    """
    获取指定数据源的新闻
    
    Args:
        source_id: 数据源 ID
    
    Returns:
        新闻列表
    
    Raises:
        ValueError: 如果数据源不存在
    """
    pass
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_sources.py -v

# 测试覆盖率
pytest --cov=news_aggregator tests/
```

## 📋 Pull Request 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] Commit message 符合规范

## 🙋 问答

**Q: 如何添加新的数据源？**
A: 参考 `sources/bilibili_hotword.py`，创建新文件并使用 `@register_source` 装饰器

**Q: 如何调试？**
A: 设置环境变量 `DEBUG=1`，查看详细日志

**Q: 如何报告安全问题？**
A: 请发送邮件到 security@example.com（待配置）

---

再次感谢你的贡献！🦊
