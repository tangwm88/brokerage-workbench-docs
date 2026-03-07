# 业绩面板组件

## 组件信息

| 项目 | 内容 |
|------|------|
| 组件名称 | PerformancePanel |
| 组件路径 | components/business/PerformancePanel.vue |
| 优先级 | P0 |
| 状态 | 已完成 |

---

## 组件截图

```
┌─────────────────────────────────────┐
│  3月 业绩概览              65% ○   │
├─────────────────────────────────────┤
│  12    8      5      50.0          │
│ 新增   签约   开户   收入(万)       │
│  ↑20%  ↑33%   -      -             │
├─────────────────────────────────────┤
│  📋 待办 20    ⏰ 今日跟进 5        │
└─────────────────────────────────────┘
```

---

## Props

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| data | Object | 是 | 业绩数据 |
| data.newCustomers | Number | 是 | 新增客户数 |
| data.signedCustomers | Number | 是 | 签约客户数 |
| data.accountOpenings | Number | 是 | 开户数 |
| data.revenue | Number | 是 | 收入（分） |
| data.completionRate | Number | 是 | 完成率百分比 |
| data.pendingTasks | Number | 否 | 待办数量 |
| data.todayFollowups | Number | 否 | 今日跟进数 |

---

## Events

| 事件 | 说明 | 参数 |
|------|------|------|
| view-detail | 查看详情 | type: 'new'|'signed'|'account'|'revenue' |

---

## 使用示例

```vue
<template>
  <PerformancePanel 
    :data="performanceData"
    @view-detail="handleViewDetail"
  />
</template>

<script setup>
const performanceData = {
  newCustomers: 12,
  newCustomersTrend: 20,
  signedCustomers: 8,
  signedCustomersTrend: 33,
  accountOpenings: 5,
  revenue: 500000, // 分
  completionRate: 65,
  pendingTasks: 20,
  todayFollowups: 5
}

function handleViewDetail(type) {
  console.log('查看详情:', type)
}
</script>
```

---

## 样式规范

### 色彩
- 背景：渐变（#667eea → #764ba2）
- 文字：#ffffff
- 趋势上升：rgba(7, 193, 96, 0.3)
- 趋势下降：rgba(238, 10, 36, 0.3)

### 字体
- 月份：24px, 700
- 数字：20px, 700
- 标签：12px
- 趋势：11px

### 间距
- 内边距：20px 16px
- 指标间距：12px
- 底部统计间距：24px

---

## 交互

- 点击业绩指标：触发 view-detail 事件
- 完成率环形图：中心显示百分比

---

*最后更新：2026-03-06*