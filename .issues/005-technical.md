# Issue #5: 技术面分析

## What to build

实现 MACD、KDJ、RSI、均线系统等技术指标计算，在个股详情页展示 K 线图和技术指标。

## Acceptance criteria

- [ ] 定义 TechnicalAnalysis 模型：stock_id, macd_signal, kdj_signal, rsi_14, ma_trend, ma5, ma10, ma20, ma60, technical_score, analysis_date
- [ ] 实现技术指标计算服务（基于 ta-lib 或手动计算）
- [ ] 技术评分逻辑：MACD金叉+10, KDJ金叉+10, RSI<30超卖+15, 均线多头排列+15 等
- [ ] 实现 GET `/api/analysis/technical/{code}` 接口
- [ ] 个股详情页展示：ECharts K线图 + MACD/KDJ/RSI 副图
- [ ] 均线叠加显示在 K 线图上
- [ ] 技术信号标签：买入/持有/卖出

## Technical Notes

- ECharts K 线图使用 candlestick 类型
- 技术指标计算可用 `ta` 库或 `pandas_ta`
- K 线图支持缩放、拖拽

## Blocked by

#3 - 每日行情数据
