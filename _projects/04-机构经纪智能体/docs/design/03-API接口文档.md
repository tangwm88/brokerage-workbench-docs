# 机构经纪员工端工作台 - API接口文档

**版本**：v1.0  
**日期**：2026-03-06  
**协议**：RESTful API + WebSocket

---

## 目录

1. [接口规范](#一接口规范)
2. [认证授权](#二认证授权)
3. [工作台接口](#三工作台接口)
4. [客户管理接口](#四客户管理接口)
5. [开户流程接口](#五开户流程接口)
6. [任务管理接口](#六任务管理接口)
7. [请示协同接口](#七请示协同接口)
8. [智能体对话接口](#八智能体对话接口)
9. [通用接口](#九通用接口)
10. [错误码定义](#十错误码定义)

---

## 一、接口规范

### 1.1 基本信息

| 项目 | 说明 |
|------|------|
| 协议 | HTTPS |
| 格式 | JSON |
| 编码 | UTF-8 |
| 时间格式 | ISO 8601 (YYYY-MM-DDTHH:mm:ssZ) |
| 日期格式 | YYYY-MM-DD |
| 金额单位 | 分（人民币）|

### 1.2 请求规范

**请求头**

```http
Content-Type: application/json
Authorization: Bearer {access_token}
X-Request-ID: {uuid}
X-Client-Version: 1.0.0
```

**分页参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| pageSize | int | 否 | 每页条数，默认20，最大100 |
| sortField | string | 否 | 排序字段 |
| sortOrder | string | 否 | 排序方向：asc/desc |

**分页响应**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

### 1.3 响应规范

**成功响应**

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**错误响应**

```json
{
  "code": 10001,
  "message": "参数错误",
  "data": {
    "field": "customerName",
    "detail": "客户名称不能为空"
  }
}
```

---

## 二、认证授权

### 2.1 登录接口

**POST /auth/login**

**请求体**

```json
{
  "username": "zhangsan",
  "password": "encrypted_password",
  "captcha": "1234",
  "captchaKey": "uuid"
}
```

**响应**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 7200,
    "user": {
      "id": "EMP001",
      "name": "张三",
      "department": "机构经纪部",
      "role": "客户经理",
      "permissions": ["customer:create", "account:apply"]
    }
  }
}
```

### 2.2 刷新Token

**POST /auth/refresh**

**请求体**

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 2.3 登出

**POST /auth/logout**

---

## 三、工作台接口

### 3.1 获取业绩摘要

**GET /api/v1/dashboard/summary**

**响应**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "currentPeriod": {
      "type": "month",
      "startDate": "2024-03-01",
      "endDate": "2024-03-31"
    },
    "newCustomers": 12,
    "newCustomersTrend": 20,
    "signedCustomers": 8,
    "signedCustomersTrend": 33,
    "accountOpenings": 5,
    "accountOpeningsTrend": 0,
    "tradingVolume": 150000000,
    "revenue": 500000,
    "monthlyTarget": {
      "newCustomers": 20,
      "signedCustomers": 15,
      "revenue": 1000000
    },
    "completionRate": 65
  }
}
```

### 3.2 获取待办列表

**GET /api/v1/dashboard/todos**

**查询参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | int | 否 | 返回条数，默认10 |
| priority | string | 否 | 优先级筛选：urgent/high/normal/low |
| type | string | 否 | 类型筛选：customer_follow/account_open/collaboration |

**响应**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "urgentCount": 3,
    "highCount": 5,
    "normalCount": 12,
    "list": [
      {
        "id": "TASK001",
        "taskNo": "T20240306001",
        "title": "跟进XX投资管理有限公司",
        "description": "客户已表达开户意向，需尽快推进",
        "type": "customer_follow",
        "priority": "urgent",
        "customerId": "C001",
        "customerName": "XX投资管理有限公司",
        "dueDate": "2024-03-07",
        "dueTime": "17:00:00",
        "isOverdue": false,
        "overdueHours": 0,
        "aiSuggestion": "建议今日下午致电客户，确认材料准备情况"
      }
    ]
  }
}
```

### 3.3 获取最近客户

**GET /api/v1/dashboard/recent-customers**

**响应**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "C001",
      "customerNo": "C20240306001",
      "customerName": "XX投资管理有限公司",
      "customerType": "机构",
      "status": "ongoing",
      "stage": "意向",
      "lastContactDate": "2024-03-05",
      "nextFollowupDate": "2024-03-07"
    }
  ]
}
```

---

## 四、客户管理接口

### 4.1 客户列表

**GET /api/v1/customers**

### 4.2 客户详情

**GET /api/v1/customers/{id}**

### 4.3 创建客户

**POST /api/v1/customers**

### 4.4 客户查重

**POST /api/v1/customers/check-duplicate**

**响应**

```json
{
  "code": 0,
  "data": {
    "isDuplicate": false,
    "confidence": 0.85,
    "similarCustomers": [],
    "suggestion": "未发现重复客户，可以继续录入。"
  }
}
```

### 4.5 生成AI画像

**POST /api/v1/customers/generate-profile**

---

## 五、开户流程接口

### 5.1 提交开户申请

**POST /api/v1/account-openings**

### 5.2 开户申请列表

**GET /api/v1/account-openings**

### 5.3 AI预审

**POST /api/v1/account-openings/{id}/pre-check**

### 5.4 查询开户进度

**GET /api/v1/account-openings/{id}/status**

---

## 六、任务管理接口

### 6.1 任务列表

**GET /api/v1/tasks**

### 6.2 创建任务

**POST /api/v1/tasks**

---

## 七、请示协同接口

### 7.1 请示列表

**GET /api/v1/collaborations**

### 7.2 创建请示

**POST /api/v1/collaborations**

### 7.3 AI生成请示草稿

**POST /api/v1/collaborations/generate-draft**

---

## 八、智能体对话接口

### 8.1 HTTP对话

**POST /api/v1/agent/chat**

**请求体**

```json
{
  "message": "我想查看我的客户列表",
  "sessionId": "session_123",
  "context": {}
}
```

**响应**

```json
{
  "code": 0,
  "data": {
    "type": "card",
    "content": "为您查询到以下客户：",
    "data": {
      "cardType": "customer_list",
      "customers": []
    },
    "actions": [
      { "id": "view_all", "text": "查看全部", "type": "navigate", "path": "/customers" }
    ]
  }
}
```

### 8.2 WebSocket连接

**WS /ws/agent/chat?sessionId={sessionId}**

---

## 九、通用接口

### 9.1 文件上传

**POST /api/v1/files/upload**

### 9.2 获取配置

**GET /api/v1/config**

---

## 十、错误码定义

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0 | 成功 | - |
| 10001 | 参数错误 | 检查请求参数 |
| 10002 | 未授权 | 重新登录 |
| 10003 | 权限不足 | 联系管理员 |
| 10004 | 资源不存在 | 检查资源ID |
| 10005 | 资源重复 | 检查重复条件 |
| 20001 | 客户查重-已存在 | 联系归属人协同 |
| 20002 | 开户预审-不通过 | 补充材料后重试 |
| 30001 | 底座接口异常 | 稍后重试 |
| 50001 | 系统内部错误 | 联系技术支持 |

---

*文档版本：v1.0*  
*最后更新：2026-03-06*