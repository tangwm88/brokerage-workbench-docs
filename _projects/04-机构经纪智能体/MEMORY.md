# MEMORY.md - 机构经纪智能体

## 项目概述

**项目名称**: 机构经纪智能体  
**所属业务线**: 机构经纪  
**目标**: 客户开发、开户、交易服务、客户服务AI化  
**状态**: 进行中（文档已迁移，待开发实施）

---

## 已完成的文档工作

### 2026-03-06 文档迁移完成

将主workspace中的机构经纪相关文档迁移到本项目空间：

**design/ 目录** (7个文档):
- 员工端工作台实现方案_v1.1 - 一个月MVP实现方案
- 前端H5组件设计 - Vue3项目结构和组件代码
- API接口文档 - RESTful和WebSocket接口规范
- 底座SDK封装代码 - 语料/网络/身份/风控SDK
- 部署脚本 - Docker Compose和CI/CD配置
- 服务智能体方案_v1.0 - 整体业务方案
- 技术设计文档_v1.0 - 技术架构详细设计

**planning/ 目录** (5个文档):
- 平台建设开发方案_V2.0 - Part1-3完整版
- OpenClaw本地化建设方案_V1.0
- 本地化技术实施方案_V1.0
- AI施工两周冲刺方案
- AI施工实操细则手册

---

## 关键决策

1. **技术栈**: OpenClaw + Vue3 + PostgreSQL + Docker
2. **实现方式**: 自动化(OpenClaw) + 智能体调用 双轨并行
3. **时间线**: 4周MVP（基础→核心→闭环→上线）

---

## 下一步行动

- [ ] 启动开发实施
- [ ] 搭建开发环境
- [ ] 底座对接测试
- [ ] 前端页面开发
- [ ] 后端API开发
- [ ] 联调测试

---

## 关联资源

### GitHub仓库
- **文档仓库**: https://github.com/tangwm88/brokerage-workbench-docs
  - 包含：一个月实现方案、前端H5设计、API文档、底座SDK、部署脚本

### 原型页面（GitHub Pages）
- **主入口**: https://tangwm88.github.io/brokerage-ai-prototype/
- **机构经纪工作台**: https://tangwm88.github.io/brokerage-ai-prototype/institutional_brokerage_chat/
- **历史版本（白色背景）**: https://tangwm88.github.io/brokerage-ai-prototype/index_v1.html
- **AI助理工作空间**: https://tangwm88.github.io/brokerage-ai-prototype/ai_assistants/

### 备注
- 以上链接需长期维护
- 原型页面用于产品演示和测试
- 文档仓库用于技术方案存档