# Issue #13: 市场概览

## What to build

展示市场整体估值水平、情绪指标等宏观概览信息。

## Acceptance criteria

- [ ] 定义 MarketOverview 模型：date, total_market_cap, avg_pe, avg_pb, advance_count, decline_count, limit_up_count, limit_down_count, northbound_total_flow
- [ ] 实现市场概览数据获取服务
- [ ] 实现 GET `/api/market/overview` 接口
- [ ] 市场概览页面显示：
  - 市场总市值、平均市盈率、平均市净率
  - 涨跌家数（柱状图）
  - 涨停/跌停家数
  - 北向资金总流入
  - 市场情绪指标（贪婪/恐惧指数）
- [ ] 市场整体估值分位（历史百分位）

## Technical Notes

- 使用 AKShare 获取市场整体数据
- 情绪指标可基于涨跌比、成交量等计算

## Blocked by

#3 - 每日行情数据
