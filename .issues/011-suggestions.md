# Issue #11: 操作建议

## What to build

基于综合评分和持仓数据，生成止损、止盈、买入推荐、调仓建议、行业集中度提醒。

## Acceptance criteria

- [ ] 定义 Suggestion 模型：id, stock_id, type(stop_loss/take_profit/buy/rebalance/sector_alert), reason, priority, is_read, created_at
- [ ] 实现建议生成引擎：
  - 止损：持仓亏损 > 15%
  - 止盈：持仓盈利 > 30%
  - 买入推荐：未持仓 + 综合评分 > 80
  - 调仓建议：持仓 + 综合评分 < 40
  - 行业集中度：单一行业持仓 > 40%
- [ ] 实现 GET `/api/suggestions` 接口，返回所有建议
- [ ] 实现 POST `/api/suggestions/generate` 接口，触发建议生成
- [ ] 操作建议页面显示：建议类型、股票、原因、优先级
- [ ] 支持标记已读/忽略建议
- [ ] 建议类型用不同颜色/图标区分

## Technical Notes

- 建议每天收盘后自动重新生成
- 优先级：高（止损）> 中（止盈/调仓）> 低（买入推荐）

## Blocked by

#8 - 综合评分系统
#9 - 持仓管理
