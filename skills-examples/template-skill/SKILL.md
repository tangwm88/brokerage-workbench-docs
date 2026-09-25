---
name: my-skill
description: |
  简短、精确的触发描述。
  告诉AI在什么场景下应该加载这个skill。
  写2-3句话，覆盖关键词和触发意图。
  例如：
  "当用户需要查询GitHub仓库信息、统计数据或状态时调用此skill。"
metadata:
  openclaw:
    requires:
      bins:
        - curl  # 需要的二进制工具
        - jq    # 可选，按实际依赖填写
    install:
      - id: node
        kind: node
        package: my-cli-package
        bins: [my-cli]
        label: "Install my CLI (npm)"
---

# {Skill 标题}

一段1-2句话的能力概述。告诉AI这个skill是用来做什么的。

## 安装

### 方式一：npm（推荐）

```bash
npm install -g my-cli-package
my-cli --version
```

### 方式二：源码安装

```bash
git clone https://github.com/your-org/my-cli.git
cd my-cli
npm install
npm link
```

## 快速开始

```bash
# 最简用法示例
my-cli init
my-cli run
```

## 核心工作流

1. **步骤一**：准备工作
2. **步骤二**：执行核心操作
3. **步骤三**：验证结果
4. **步骤四**：收尾或清理

## 命令参考

### 命令分组一：基础操作

```bash
my-cli init        # 初始化
my-cli status      # 查看状态
my-cli list        # 列出所有项目
```

### 命令分组二：核心功能

```bash
my-cli create <name>    # 创建
my-cli update <id>      # 更新
my-cli delete <id>      # 删除
```

### 命令分组三：高级功能

```bash
my-cli export --format json   # 导出为JSON
my-cli import ./data.csv      # 导入CSV
my-cli sync --remote          # 同步远程数据
```

## 示例

### 示例1：常见场景

```bash
# 描述这个示例在做什么
my-cli create "example-project"
my-cli status example-project
```

### 示例2：带参数的场景

```bash
# 描述带参数的场景
my-cli export --format json --output ./result.json
```

## 故障排查

- **问题一**：错误描述和解决方法
- **问题二**：错误描述和解决方法
- **通用建议**：如果以上都不行，尝试 `my-cli doctor` 或 `my-cli --verbose`

## 注意事项

- 重要提示1
- 重要提示2
- 安全警告（如果有破坏性操作）

## 相关链接

- CLI仓库：https://github.com/your-org/my-cli
- 文档：https://docs.your-org.com/my-cli
- Issue反馈：https://github.com/your-org/my-cli/issues