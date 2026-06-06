# Issue #8: 综合评分系统

## What to build

将估值、技术面、基本面、资金流向、动量等因子加权组合，生成综合评分，支持权重调整。

## Acceptance criteria

- [ ] 定义 CompositeScore 模型：stock_id, valuation_score, technical_score, fundamental_score, capital_flow_score, momentum_score, total_score, rank, analysis_date
- [ ] 实现多因子加权评分服务，权重可配置（默认：估值25%, 技术20%, 基本面25%, 资金15%, 动量15%）
- [ ] 实现 GET `/api/analysis/composite` 接口，返回所有股票评分排名
- [ ] 实现 PUT `/api/analysis/weights` 接口，更新权重配置
- [ ] 股票总览表显示综合评分、排名、各维度分数
- [ ] 支持按评分排序、按维度筛选
- [ ] 评分等级：优秀(>80), 良好(60-80), 一般(40-60), 较差(<40)

## Technical Notes

- 评分范围统一到 0-100 分
- 动量评分：60日涨幅排名 + 年初至今涨幅排名
- 评分结果缓存，避免重复计算

## Blocked by

#4 - 估值分析
#5 - 技术面分析
#6 - 基本面分析
#7 - 资金流向分析
