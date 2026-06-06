# Issue #7: 资金流向分析

## What to build

获取主力资金、北向资金流向数据，分析资金动向，生成资金流向评分。

## Acceptance criteria

- [ ] 定义 CapitalFlowAnalysis 模型：stock_id, main_force_net, northbound_flow, margin_trading_change, capital_flow_score, analysis_date
- [ ] 使用 AKShare 获取资金流向数据
- [ ] 资金评分逻辑：主力净流入+分, 北向资金买入+分, 融资余额增加+分
- [ ] 实现 GET `/api/analysis/capital-flow/{code}` 接口
- [ ] 个股详情页显示资金流向图表
- [ ] 资金状态标签：大幅流入/小幅流入/平衡/小幅流出/大幅流出

## Technical Notes

- 资金数据每日更新
- 北向资金数据来源：沪深港通持股

## Blocked by

#3 - 每日行情数据
