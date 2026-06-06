# Issue #16: Docker 部署

## What to build

配置 Docker Compose，支持一键部署到 Linux 服务器。

## Acceptance criteria

- [ ] 创建 `backend/Dockerfile`
- [ ] 创建 `frontend/Dockerfile`
- [ ] 创建 `docker-compose.yml`，包含：
  - backend 服务（端口 8000）
  - frontend 服务（端口 80/443）
  - 数据卷挂载（SQLite 数据库持久化）
- [ ] 创建 `.env.example` 环境变量模板
- [ ] 支持 `docker-compose up -d` 一键启动
- [ ] 支持 `docker-compose down` 停止
- [ ] 前端 Nginx 配置反向代理到后端 API
- [ ] README 中添加部署说明

## Technical Notes

- 后端基础镜像：python:3.11-slim
- 前端构建后用 nginx:alpine 托管
- 数据卷：`./backend/data:/app/data`（SQLite 持久化）

## Blocked by

#15 - 定时更新
