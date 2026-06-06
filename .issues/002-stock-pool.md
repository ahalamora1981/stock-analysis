# Issue #2: 股票池导入

## What to build

将 CSV 中的 A 股行业 ETF 持仓股票导入 SQLite 数据库，实现股票池管理功能，支持手动添加/删除股票。

## Acceptance criteria

- [ ] 定义 Stock 模型：id, code, name, etf_list, is_active, created_at
- [ ] 创建数据导入脚本，读取 `stocks/A股行业ETF持仓股票.csv` 并写入数据库
- [ ] 实现 GET `/api/stocks` 接口，返回所有股票列表
- [ ] 实现 POST `/api/stocks` 接口，手动添加新股票
- [ ] 实现 DELETE `/api/stocks/{id}` 接口，删除股票
- [ ] 前端股票列表页面显示所有股票（代码、名称、所属ETF）
- [ ] 支持搜索/筛选功能

## Technical Notes

- CSV 文件路径：`stocks/A股行业ETF持仓股票.csv`
- 使用 SQLAlchemy ORM 操作 SQLite
- 数据库文件：`backend/data/stock_analysis.db`

## Blocked by

#1 - 项目脚手架
