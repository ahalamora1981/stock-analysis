# Issue #6: 基本面分析

## What to build

获取并分析股票的财务指标，包括 ROE、毛利率、营收增速、现金流等，生成基本面评分。

## Acceptance criteria

- [ ] 定义 FundamentalAnalysis 模型：stock_id, roe, gross_margin, revenue_growth, net_profit_growth, cash_flow_per_share, fundamental_score, analysis_date
- [ ] 使用 AKShare 获取财务数据（`ak.stock_financial_analysis_indicator`）
- [ ] 基本面评分逻辑：ROE>15%+高分, 毛利率>30%+分, 营收正增长+分, 现金流为正+分
- [ ] 实现 GET `/api/analysis/fundamental/{code}` 接口
- [ ] 个股详情页显示财务指标卡片
- [ ] 基本面状态标签：优秀/良好/一般/较差

## Technical Notes

- 财务数据季度更新，需缓存
- AKShare 财务数据接口可能较慢，考虑异步获取

## Blocked by

#3 - 每日行情数据
