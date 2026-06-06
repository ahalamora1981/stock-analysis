# Issue #9: 持仓管理

## What to build

实现持仓的增删改查功能，支持分批买入，记录成本价和持仓数量。

## Acceptance criteria

- [ ] 定义 Position 模型：id, stock_id, total_shares, avg_cost, total_cost, created_at, updated_at
- [ ] 定义 PositionDetail 模型（分批买入记录）：id, position_id, shares, cost_price, buy_date, note
- [ ] 实现 CRUD 接口：
  - POST `/api/positions` - 新建持仓（买入）
  - GET `/api/positions` - 获取所有持仓
  - PUT `/api/positions/{id}` - 更新持仓
  - DELETE `/api/positions/{id}` - 删除持仓
- [ ] 持仓列表页面显示：股票名称、持仓数量、成本价、最新价、盈亏金额、盈亏比例
- [ ] 支持分批买入，自动计算加权平均成本
- [ ] 持仓汇总：总资产、总成本、总盈亏、总收益率

## Technical Notes

- 每次买入创建新的 PositionDetail 记录
- 更新 Position 的 total_shares 和 avg_cost
- 盈亏计算：(最新价 - avg_cost) * total_shares

## Blocked by

#1 - 项目脚手架
