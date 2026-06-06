# Issue #12: 行业板块分析

## What to build

按行业 ETF 维度分析股票，显示各行业强弱对比。

## Acceptance criteria

- [ ] 定义 SectorAnalysis 模型：id, etf_name, avg_score, stock_count, top_stocks, trend, analysis_date
- [ ] 实现行业分析服务：按 ETF 分组计算平均评分
- [ ] 实现 GET `/api/sectors` 接口，返回行业列表
- [ ] 实现 GET `/api/sectors/{name}` 接口，返回行业详情
- [ ] 行业板块页面显示：
  - 行业列表（名称、平均评分、股票数量、趋势）
  - 行业详情（成分股列表、评分排名）
- [ ] 行业强弱排名：按平均评分排序
- [ ] 行业趋势标签：上升/平稳/下降

## Technical Notes

- 一只股票可能属于多个 ETF，需处理多对多关系
- 行业趋势可通过近 5 日平均评分变化判断

## Blocked by

#8 - 综合评分系统
