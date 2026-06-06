# Issue #1: 项目脚手架

## What to build

搭建 FastAPI + React 项目基础结构，配置 BMW M 设计风格主题，确保前后端可以正常通信。

## Acceptance criteria

- [ ] 使用 `uv init` 初始化 Python 项目，`uv add` 安装依赖（fastapi, uvicorn, sqlalchemy, akshare 等）
- [ ] FastAPI 后端运行在 localhost:8000，提供 `/api/health` 健康检查接口
- [ ] React 前端使用 Vite 创建，运行在 localhost:5173，配置代理到后端
- [ ] 实现 BMW M 设计系统 CSS（参考 DESIGN-bmw-m.md），包含颜色、字体、组件样式
- [ ] 实现侧边栏导航布局组件
- [ ] 前端可以成功调用后端 health 接口并显示状态

## Technical Notes

- Python 使用 `uv` 管理项目和依赖
- 后端目录：`backend/`
- 前端目录：`frontend/`
- BMW M 主题 CSS 放在 `frontend/src/styles/bmw-m-theme.css`

## Blocked by

None - can start immediately
