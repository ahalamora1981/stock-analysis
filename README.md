# A股行业ETF持仓分析系统

一个基于 FastAPI + React 的 A 股行业 ETF 持仓股票分析 Web 应用，提供多维度股票分析、综合评分、持仓管理和操作建议。

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [使用手册](#使用手册)
- [API 接口文档](#api-接口文档)
- [项目结构](#项目结构)
- [部署指南](#部署指南)
- [常见问题](#常见问题)
- [License](#license)

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **股票池管理** | 支持 CSV 导入 A 股行业 ETF 持仓股票，可通过代码新增，可手动删除 |
| **行情数据** | 通过腾讯行情 API 实时获取股票最新价、涨跌幅、PE、PB、市值等 |
| **多维度分析** | 估值分析、技术面分析、动量分析，综合评估股票质量 |
| **综合评分** | 多因子加权评分系统，0-100 分，权重可在设置页调整 |
| **持仓管理** | 支持分批买入/卖出，自动计算加权平均成本和盈亏 |
| **历史统计** | 记录已卖出股票的累计盈亏和收益率 |
| **操作建议** | 基于评分和持仓自动生成止损/止盈/买入/调仓/行业集中度建议 |
| **行业板块** | 按 ETF 维度分析行业强弱排名 |
| **市场概览** | 市场整体估值水平、涨跌统计、情绪指标 |
| **股票详情** | 查看单只股票完整分析报告，含各维度评分及权重 |
| **应用配置** | 可调整综合评分各维度权重，总和必须为 100% |
| **Excel 导出** | 一键导出包含股票分析和持仓数据的 Excel 报告 |

### 分析维度

| 维度 | 指标 | 权重(默认) |
|------|------|-----------|
| **估值分析** | PE 分位数、PB 分位数 | 25% |
| **技术面分析** | MA 均线趋势、MACD 金叉/死叉、KDJ 超买超卖、RSI | 20% |
| **基本面分析** | 财务指标 | 25% |
| **资金流分析** | 资金流向 | 15% |
| **动量分析** | 近期涨跌幅排名 | 15% |
| **综合评分** | 以上维度加权汇总 | 100% |

### 涨跌幅周期

股票总览和详情页展示四个周期的涨跌幅：
- **60日涨跌幅** - 近 60 个交易日累计涨跌
- **20日涨跌幅** - 近 20 个交易日累计涨跌
- **5日涨跌幅** - 近 5 个交易日累计涨跌
- **当日涨跌幅** - 今日涨跌幅

### 评分等级

| 分数区间 | 等级 | 含义 |
|----------|------|------|
| ≥ 70 | 优秀 | 估值低、趋势好，值得关注 |
| 55-69 | 良好 | 综合表现不错 |
| 40-54 | 一般 | 中性，无明显优势 |
| < 40 | 较差 | 高估或趋势弱，需谨慎 |

### 操作建议类型

| 类型 | 触发条件 | 优先级 |
|------|----------|--------|
| 止损 | 持仓亏损 > 15% | 高 |
| 止盈 | 持仓盈利 > 30% | 中 |
| 调仓 | 综合评分 < 40 | 中 |
| 行业集中度 | 单一行业持仓 > 40% | 中 |
| 买入推荐 | 未持仓 + 评分 ≥ 70 | 低 |

---

## 技术栈

### 后端

- **Python 3.12** - 主语言
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **SQLite** - 数据库（通过 aiosqlite 异步驱动）
- **openpyxl** - Excel 导出
- **uv** - Python 包管理

### 前端

- **React 18** - UI 框架
- **Vite** - 构建工具
- **React Router** - 路由

### 数据源

- **腾讯行情 API** (`qt.gtimg.cn`) - 实时行情 + 历史 K 线
- 无需 API Key，免费使用

### 部署

- **Docker Compose** - 容器化部署
- **Nginx** - 前端静态文件托管 + 反向代理

---

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- uv (Python 包管理)
- npm (Node.js 包管理)

### 1. 克隆仓库

```bash
git clone https://github.com/ahalamora1981/stock-analysis.git
cd stock-analysis
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
uv sync

# 启动服务（开发模式，自动重载）
uv run uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 启动。

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动。

### 4. 初始化数据

1. 打开浏览器访问 http://localhost:5173
2. 进入「股票总览」页面
3. 点击「运行分析」按钮，执行多维度分析
4. 进入「市场概览」页面，查看整体数据

---

## 使用手册

### 页面说明

系统包含 6 个主要页面：

#### 1. 市场概览 (Dashboard)

**路径**: `/`

显示市场整体情况：
- **总资产统计**: 总市值、平均市盈率、平均市净率
- **市场情绪**: 贪婪/恐惧指数（基于涨跌比计算）
- **涨跌统计**: 上涨/下跌/平盘家数，涨停/跌停家数
- **评分分布**: 优秀/良好/一般/较差各多少只
- **Excel 导出**: 点击按钮导出分析报告

#### 2. 股票总览 (Stock List)

**路径**: `/stocks`

显示所有股票的综合评分和排名：
- **搜索**: 支持按代码、名称、ETF 搜索
- **排序**: 点击表头可按排名、评分、涨跌幅、估值、技术面排序（升序/降序切换）
- **多周期涨跌幅**: 60日、20日、5日、当日涨跌幅
- **新增股票**: 点击「新增股票」按钮，输入代码验证后添加
- **删除股票**: 点击行末红色删除按钮
- **查看详情**: 点击任意股票行跳转到详情页
- **更新行情**: 拉取最新行情数据
- **运行分析**: 执行多维度分析并更新评分

#### 3. 股票详情 (Stock Detail)

**路径**: `/stocks/:code`

查看单只股票完整分析：
- **行情概要**: 最新价、60/20/5/当日涨跌幅、PE、PB、总市值
- **综合评分构成**: 各维度分数条、权重、加权得分
- **估值分析**: PE/PB 及历史分位数
- **技术面分析**: MA、MACD、KDJ、RSI 指标详情
- **权重配置**: 当前使用的权重，可跳转设置页调整

#### 4. 行业板块 (Sectors)

**路径**: `/sectors`

按 ETF 维度显示行业分析：
- **行业卡片**: 每个行业一张卡片，显示平均评分和趋势
- **趋势箭头**: ↑ 上升 / → 平稳 / ↓ 下降
- **成分股**: 每个行业显示 Top 5 评分最高的股票

#### 5. 我的持仓 (Positions)

**路径**: `/positions`

管理个人持仓：
- **资产概览**: 持仓总资产、总成本、盈亏、收益率、历史盈亏
- **买入**: 点击「买入股票」，输入代码、数量、价格
- **卖出**: 点击持仓行右侧「卖出」按钮，输入数量和价格
- **重置**: 清空所有持仓和交易记录
- **交易历史**: 查看所有买入/卖出记录

**持仓统计说明**:
| 指标 | 含义 |
|------|------|
| 持仓总资产 | 当前持有股票的市值 |
| 持仓总成本 | 买入这些股票的总花费 |
| 持仓总盈亏 | 市值 - 成本（未实现盈亏） |
| 持仓收益率 | 盈亏 / 成本 × 100% |
| 历史总盈亏 | 已卖出股票的累计盈亏 |
| 历史总收益率 | 累计盈亏 / 累计投入 × 100% |

#### 6. 操作建议 (Suggestions)

**路径**: `/suggestions`

显示系统生成的投资建议：
- **生成建议**: 点击按钮重新分析并生成建议
- **建议类型**: 止损、止盈、买入推荐、调仓、行业集中度
- **优先级**: 高(止损) > 中(止盈/调仓) > 低(买入推荐)

#### 7. 应用配置 (Settings)

**路径**: `/settings`

调整综合评分权重：
- **估值**: 默认 25%
- **技术面**: 默认 20%
- **基本面**: 默认 25%
- **资金流**: 默认 15%
- **动量**: 默认 15%
- **权重总和**: 必须为 100%，不满足时红底白字提示
- **未保存提示**: 修改权重后显示红色「修改未保存」
- **恢复默认**: 一键恢复默认权重

### 数据更新流程

推荐的使用流程：

```
1. 更新行情 → 拉取最新股价
2. 运行分析 → 计算各维度评分
3. 生成建议 → 基于评分和持仓生成操作建议
4. 查看建议 → 参考建议决定是否操作
5. 执行交易 → 在持仓页面买入/卖出
```

### 评分计算逻辑

**估值评分** (0-100):
- PE/PB 在历史数据中的分位数
- 分位数越低（越便宜），评分越高
- 公式: `估值分 = (100 - PE分位) × 0.6 + (100 - PB分位) × 0.4`

**技术面评分** (0-100):
- 基础分 50 分
- MA 多头排列: +15 分
- MACD 金叉: +15 分
- KDJ 超卖金叉: +10 分
- RSI 超卖(<30): +10 分
- 反之扣分

**综合评分**:
```
综合分 = 估值分 × 估值权重 + 技术分 × 技术权重 + 基本面分 × 基本面权重 + 资金流分 × 资金流权重 + 动量分 × 动量权重
```

### 颜色说明

采用中国股市惯例：
- **红色** = 上涨 / 盈利
- **绿色** = 下跌 / 亏损

评分徽章颜色：
- 🟥 红色 = 优秀 (≥70)
- 🟦 蓝色 = 良好 (55-69)
- 🟨 黄色 = 一般 (40-54)
- 🟩 绿色 = 较差 (<40)

---

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

### 股票管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stocks` | GET | 获取股票列表 |
| `/api/stocks/with-latest` | GET | 获取股票列表（含最新行情+多周期涨跌幅） |
| `/api/stocks` | POST | 添加股票 |
| `/api/stocks/add-by-code?code=` | POST | 通过代码添加股票 |
| `/api/stocks/check-code?code=` | GET | 验证股票代码有效性 |
| `/api/stocks/{id}` | DELETE | 删除股票 |

### 行情数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/data/fetch` | POST | 拉取所有股票行情 |
| `/api/data/daily/{code}` | GET | 获取历史日线数据 |

### 分析

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/analysis/run` | POST | 运行分析（估值+技术+评分） |
| `/api/analysis/composite` | GET | 获取综合评分列表 |
| `/api/analysis/valuation/{code}` | GET | 获取估值详情 |
| `/api/analysis/technical/{code}` | GET | 获取技术面详情 |
| `/api/analysis/detail/{code}` | GET | 获取股票完整分析详情 |

### 持仓管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/positions` | GET | 获取持仓列表 |
| `/api/positions/buy` | POST | 买入股票 |
| `/api/positions/sell` | POST | 卖出股票 |
| `/api/positions/reset` | POST | 重置所有数据 |
| `/api/positions/history` | GET | 获取历史统计 |
| `/api/positions/transactions` | GET | 获取交易历史 |

### 其他

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/suggestions` | GET | 获取操作建议 |
| `/api/suggestions/generate` | POST | 生成操作建议 |
| `/api/sectors` | GET | 获取行业板块 |
| `/api/market/overview` | GET | 获取市场概览 |
| `/api/config` | GET | 获取权重配置 |
| `/api/config` | POST | 保存权重配置 |
| `/api/export/excel` | GET | 导出 Excel 报告 |

---

## 项目结构

```
stock-analysis/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口，中间件配置
│   │   ├── config.py            # 配置（数据库路径、API 前缀）
│   │   ├── database.py          # SQLite 异步连接
│   │   ├── models/
│   │   │   ├── stock.py         # 股票模型
│   │   │   ├── daily_data.py    # 日线数据模型
│   │   │   ├── analysis.py      # 分析结果模型（估值/技术/综合）
│   │   │   ├── position.py      # 持仓/交易/建议/历史模型
│   │   │   └── config.py        # 应用配置模型（权重）
│   │   ├── routers/
│   │   │   ├── stocks.py        # 股票管理 API
│   │   │   ├── data.py          # 行情数据 API
│   │   │   ├── analysis.py      # 分析评分 API
│   │   │   ├── positions.py     # 持仓交易 API
│   │   │   ├── suggestions.py   # 操作建议 API
│   │   │   ├── sectors.py       # 行业板块 API
│   │   │   ├── market.py        # 市场概览 API
│   │   │   ├── export.py        # Excel 导出 API
│   │   │   └── config.py        # 配置 API
│   │   ├── schemas/
│   │   │   └── stock.py         # Pydantic 数据模型
│   │   └── services/
│   │       ├── data_fetcher.py  # 腾讯行情 API 数据获取
│   │       ├── analyzer.py      # 估值/技术分析引擎
│   │       ├── scorer.py        # 多因子综合评分（读取配置权重）
│   │       ├── suggestion.py    # 操作建议生成
│   │       └── import_csv.py    # CSV 导入脚本
│   ├── data/
│   │   └── stock_analysis.db    # SQLite 数据库文件
│   ├── Dockerfile
│   ├── pyproject.toml           # Python 依赖配置
│   └── uv.lock                  # 依赖锁文件
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.jsx       # 侧边栏布局组件
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # 市场概览页
│   │   │   ├── StockList.jsx    # 股票总览页
│   │   │   ├── StockDetail.jsx  # 股票详情页
│   │   │   ├── Sectors.jsx      # 行业板块页
│   │   │   ├── Positions.jsx    # 持仓管理页
│   │   │   ├── Suggestions.jsx  # 操作建议页
│   │   │   └── Settings.jsx     # 应用配置页
│   │   ├── styles/
│   │   │   └── bmw-m-theme.css  # BMW M 设计系统 CSS
│   │   ├── App.jsx              # 路由配置
│   │   └── main.jsx             # 入口文件
│   ├── nginx.conf               # Nginx 反向代理配置
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js           # Vite 配置（代理到后端）
├── stocks/
│   └── A股行业ETF持仓股票.csv   # 初始股票池
├── docker-compose.yml           # Docker 部署配置
├── DESIGN-bmw-m.md              # BMW M 设计规范
├── README.md
└── .gitignore
```

---

## 部署指南

### Docker Compose 部署

#### 前置条件

- Docker 20.10+
- Docker Compose 2.0+

#### 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/ahalamora1981/stock-analysis.git
cd stock-analysis

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

服务启动后：
- 前端: http://localhost
- 后端 API: http://localhost:8000

### Linux 服务器部署

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 克隆仓库
git clone https://github.com/ahalamora1981/stock-analysis.git
cd stock-analysis

# 3. 构建并启动
docker-compose up -d --build

# 4. 设置开机自启
sudo systemctl enable docker
```

---

## 常见问题

### Q: 为什么有些股票的评分为 50 分？

A: 50 分是默认中性分。当某只股票的历史数据不足（少于 20 个交易日）时，估值和技术面分析无法计算，会使用默认值 50 分。

### Q: 行情数据多久更新一次？

A: 行情数据需要手动点击「更新行情」按钮拉取。建议在每日收盘后（15:00 之后）更新。

### Q: 如何添加新的股票到分析池？

A: 在「股票总览」页面点击「新增股票」按钮，输入股票代码后点击「验证」，系统会自动获取股票名称，确认后添加。

### Q: 如何调整评分权重？

A: 进入「应用配置」页面，拖动滑块或输入数字调整各维度权重，总和必须为 100%，保存后需重新「运行分析」生效。

### Q: 重置按钮会清除什么数据？

A: 重置会清除：
- 所有持仓记录
- 所有交易历史
- 历史盈亏统计

不会清除：
- 股票池数据
- 行情数据
- 分析评分数据

### Q: Docker 部署后如何更新代码？

```bash
git pull
docker-compose up -d --build
```

---

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
