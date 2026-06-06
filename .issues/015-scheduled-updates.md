# Issue #15: 定时更新

## What to build

实现每日收盘后自动更新股票数据的定时任务。

## Acceptance criteria

- [ ] 实现定时任务服务，使用 APScheduler
- [ ] 每日 15:30（收盘后）自动执行：
  - 获取所有股票最新行情数据
  - 更新估值分析
  - 更新技术分析
  - 重新生成操作建议
- [ ] 实现 GET `/api/scheduler/status` 接口，查看任务状态
- [ ] 实现 POST `/api/scheduler/trigger` 接口，手动触发更新
- [ ] 前端显示数据更新状态和最后更新时间
- [ ] 更新日志记录

## Technical Notes

- 使用 `apscheduler` 库
- 考虑中国时区 (Asia/Shanghai)
- 更新失败时记录错误并重试

## Blocked by

#3 - 每日行情数据
