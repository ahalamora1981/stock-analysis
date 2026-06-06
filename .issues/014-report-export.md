# Issue #14: 报告导出

## What to build

支持导出 PDF/Excel 格式的分析报告。

## Acceptance criteria

- [ ] 实现 GET `/api/export/excel` 接口，导出 Excel 报告
- [ ] 实现 GET `/api/export/pdf` 接口，导出 PDF 报告
- [ ] Excel 报告包含：
  - 股票列表 sheet（代码、名称、评分、各维度分数）
  - 持仓 sheet（持仓详情、盈亏）
  - 建议 sheet（操作建议列表）
- [ ] PDF 报告包含：
  - 市场概览摘要
  - 持仓汇总
  - Top 10 推荐股票
  - 操作建议
- [ ] 前端导出按钮，支持选择导出格式

## Technical Notes

- Excel 使用 openpyxl 或 xlsxwriter
- PDF 使用 reportlab 或 weasyprint
- 报告样式与 BMW M 主题一致

## Blocked by

#8 - 综合评分系统
