# Issue #3: 每日行情数据

## What to build

使用 AKShare 获取股票每日收盘行情数据，存储到数据库，在股票列表中显示实时价格。

## Acceptance criteria

- [ ] 定义 StockDailyData 模型：stock_id, date, open, high, low, close, volume, amount, turnover_rate, pe_ttm, pb, market_cap, change_pct
- [ ] 实现 AKShare 数据获取服务，支持批量获取所有股票的日线数据
- [ ] 实现 POST `/api/data/fetch` 接口，触发数据更新
- [ ] 实现 GET `/api/stocks/{code}/daily` 接口，获取历史日线数据
- [ ] 股票列表显示：最新价、涨跌幅、市盈率、市净率、总市值
- [ ] 数据去重：同一天的数据不重复插入

## Technical Notes

- 使用 `ak.stock_zh_a_spot_em()` 获取实时行情
- 使用 `ak.stock_zh_a_hist(symbol, period="daily")` 获取历史数据
- 数据量较大时使用批量插入

## Blocked by

#2 - 股票池导入
