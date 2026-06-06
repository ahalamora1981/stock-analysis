# Issue #10: 交易历史

## What to build

记录所有买卖操作的历史，在持仓页面展示交易记录列表。

## Acceptance criteria

- [ ] 定义 Transaction 模型：id, stock_id, type(buy/sell), shares, price, total_amount, fee, date, note
- [ ] 实现交易记录接口：
  - POST `/api/transactions` - 新增交易记录
  - GET `/api/transactions` - 获取交易历史（支持按股票、日期筛选）
  - GET `/api/transactions/summary` - 交易统计
- [ ] 买入时自动创建/更新持仓
- [ ] 卖出时自动更新持仓（减少数量）
- [ ] 交易历史页面显示：日期、股票、类型、数量、价格、金额、备注
- [ ] 交易统计：总买入金额、总卖出金额、交易次数

## Technical Notes

- 交易和持仓更新在同一事务中完成
- 卖出时如果持仓不足，提示错误

## Blocked by

#9 - 持仓管理
