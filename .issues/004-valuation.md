# Issue #4: 估值分析

## What to build

对每只股票进行估值分析，计算 PE/PB 历史分位数，生成估值评分。

## Acceptance criteria

- [ ] 定义 ValuationAnalysis 模型：stock_id, pe_percentile, pb_percentile, dividend_yield, valuation_score, analysis_date
- [ ] 实现估值分析服务：计算 PE/PB 在历史数据中的分位数
- [ ] 估值评分逻辑：PE分位<30%=低估(高分)，30-70%=合理(中分)，>70%=高估(低分)
- [ ] 实现 GET `/api/analysis/valuation/{code}` 接口
- [ ] 股票列表增加估值评分列，支持按估值排序
- [ ] 估值状态标签：低估/合理/高估

## Technical Notes

- 分位数计算需要至少 250 个交易日的历史数据
- 股息率从 AKShare 获取

## Blocked by

#3 - 每日行情数据
