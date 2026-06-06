# A股行业ETF持仓分析系统

一个基于 FastAPI + React 的 A 股行业 ETF 持仓股票分析 Web 应用，提供多维度股票分析、综合评分、持仓管理和操作建议。

## 功能特性

- **股票池管理** - 支持 CSV 导入 A 股行业 ETF 持仓股票，可手动增删
- **行情数据** - 实时获取股票行情（腾讯行情 API）
- **多维度分析**
  - 估值分析：PE/PB 历史分位数
  - 技术面分析：MA、MACD、KDJ、RSI 指标
  - 动量分析：近期涨跌幅排名
- **综合评分** - 多因子加权评分系统，支持权重调整
- **持仓管理** - 支持分批买入/卖出，自动计算盈亏
- **历史统计** - 记录历史交易盈亏和收益率
- **操作建议** - 止损/止盈/买入推荐/调仓/行业集中度提醒
- **行业板块** - 按 ETF 维度分析行业强弱
- **市场概览** - 市场整体估值、情绪指标
- **Excel 导出** - 一键导出分析报告

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy + SQLite
- **前端**: React + Vite + ECharts
- **数据源**: 腾讯行情 API
- **部署**: Docker Compose

## 快速开始

### 本地开发

```bash
# 后端
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### Docker 部署

```bash
docker-compose up -d
```

访问 http://localhost

## 项目结构

```
stock-analysis/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── models/          # 数据模型
│   │   ├── routers/         # API 路由
│   │   └── services/        # 业务逻辑
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # 布局组件
│   │   ├── pages/           # 页面组件
│   │   └── styles/          # BMW M 设计系统
│   ├── nginx.conf
│   └── Dockerfile
├── stocks/
│   └── A股行业ETF持仓股票.csv
├── docker-compose.yml
└── README.md
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/stocks` | GET/POST/DELETE | 股票管理 |
| `/api/data/fetch` | POST | 获取行情数据 |
| `/api/analysis/run` | POST | 运行分析 |
| `/api/analysis/composite` | GET | 综合评分 |
| `/api/positions` | GET | 持仓列表 |
| `/api/positions/buy` | POST | 买入 |
| `/api/positions/sell` | POST | 卖出 |
| `/api/positions/reset` | POST | 重置所有数据 |
| `/api/positions/history` | GET | 历史统计 |
| `/api/suggestions` | GET | 操作建议 |
| `/api/sectors` | GET | 行业板块 |
| `/api/market/overview` | GET | 市场概览 |
| `/api/export/excel` | GET | 导出 Excel |

## 颜色说明

采用中国股市惯例：
- **红色** = 上涨/盈利
- **绿色** = 下跌/亏损

## License

MIT
