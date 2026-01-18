# GitHub Actions 配置指南

本指南说明如何使用 GitHub Actions 实现每天自动签到。

## 功能特性

- ✅ 每天早上 8 点（北京时间）自动执行签到
- ✅ 支持 GitHub Secrets 安全存储敏感信息
- ✅ 自动安装依赖和运行程序
- ✅ 保存 session 文件以便下次使用
- ✅ 支持手动触发签到
- ✅ 查看执行日志

## 配置步骤

### 1. 准备工作

确认你已经将代码推送到 GitHub 仓库。

### 2. 设置 GitHub Secrets

由于 `config.yaml` 包含敏感信息（邮箱密码、代理配置等），我们需要使用 GitHub Secrets 来安全存储这些信息。

1. 访问你的 GitHub 仓库
2. 点击 **Settings** (设置)
3. 在左侧菜单中选择 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 按钮添加以下 secrets：

#### 必需的 Secrets

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `EMAIL_ADDRESS` | 你的 Gmail 地址 | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | Gmail 应用专用密码 | `abcd efgh ijkl mnop` |

#### 可选的 Secrets（如果需要代理）

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `PROXY_HOST` | SOCKS5 代理服务器地址 | `192.168.1.237` |
| `PROXY_PORT` | SOCKS5 代理端口 | `7898` |

#### 如何添加 Secret

1. 点击 **New repository secret**
2. **Name** 输入 Secret 名称（如 `EMAIL_ADDRESS`）
3. **Secret** 输入对应的值
4. 点击 **Add secret**

重复以上步骤添加所有需要的 secrets。

### 3. 配置时间（可选）

默认配置是每天早上 8 点（北京时间）执行。如果你想修改执行时间，编辑 `.github/workflows/daily-checkin.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间，北京时间早上 8 点
```

**Cron 表达式说明**：
- 格式：`分 时 日 月 周`
- `0 0 * * *` = 每天 UTC 0:00（北京时间 8:00）
- `0 1 * * *` = 每天 UTC 1:00（北京时间 9:00）
- `0 22 * * *` = 每天 UTC 22:00（北京时间次日 6:00）

**在线 Cron 生成器**：https://crontab.guru/

### 4. 提交 workflow 文件

将 `.github/workflows/daily-checkin.yml` 文件提交到仓库：

```bash
git add .github/workflows/daily-checkin.yml
git commit -m "Add GitHub Actions workflow for daily check-in"
git push origin main
```

## 使用方法

### 自动执行（每天定时）

- 工作流会在每天早上 8 点（北京时间）自动执行
- 无需任何操作

### 手动触发

如果你想立即测试签到功能：

1. 访问你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 "GLaDOS Daily Check-in" 工作流
4. 点击 **Run workflow** 按钮
5. 选择分支（通常是 `main`）
6. 点击绿色的 **Run workflow** 按钮

### 查看执行结果

1. 访问你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 可以看到所有的工作流运行记录
4. 点击具体的运行记录可以查看详细日志

## 工作流详情

### 执行步骤

1. **Checkout code** - 检出代码
2. **Set up Python** - 设置 Python 3.11 环境
3. **Install dependencies** - 安装依赖包
4. **Create config file** - 从 Secrets 创建配置文件
5. **Run check-in** - 执行签到脚本
6. **Upload artifacts** - 上传 session 文件和日志

### Artifacts（工件）

每次运行后，会保存以下文件：
- **glados-session**: session.json 文件（保留 7 天）
- **checkin-logs**: 日志文件（保留 30 天）

## 故障排除

### 问题：工作流没有按时执行

**可能原因**：
1. GitHub Actions 有延迟（通常最多延迟 5 分钟）
2. Cron 表达式配置错误

**解决方案**：
- 检查 cron 表达式是否正确
- 查看 Actions 页面确认工作流是否被触发

### 问题：签到失败

**解决方案**：
1. 点击工作流运行记录查看详细日志
2. 检查 GitHub Secrets 是否正确配置
3. 确认邮箱应用密码有效
4. 检查代理配置（如果使用）

### 问题：无法连接到 Gmail

**解决方案**：
1. 确认 IMAP 已开启：https://mail.github.com/mail/u/0/#settings/fwdandpop
2. 使用应用专用密码而非账户密码
3. 如果需要代理，确认 `PROXY_HOST` 和 `PROXY_PORT` 正确配置

## 安全建议

1. ✅ **永远不要将敏感信息提交到代码仓库**
   - 使用 GitHub Secrets 存储密码
   - `config.yaml` 已在 `.gitignore` 中

2. ✅ **定期更换密码**
   - 建议每 3-6 个月更换一次应用密码

3. ✅ **监控 Actions 日志**
   - 定期查看工作流执行情况
   - 发现异常及时处理

## 高级配置

### 添加多个账户

如果需要管理多个 GLaDOS 账户，可以创建多个 workflow 文件：

1. 复制 `daily-checkin.yml` 为 `daily-checkin-account2.yml`
2. 添加新的 secrets（如 `EMAIL_ADDRESS_2`, `EMAIL_PASSWORD_2`）
3. 修改 cron 表达式使其错开执行时间

### 发送签到通知（可选）

如果想在签到成功后收到通知，可以在 workflow 中添加邮件发送或 webhook 通知步骤。

### 更多配置选项

参考 GitHub Actions 官方文档：
https://docs.github.com/en/actions

## 常见问题

**Q: GitHub Actions 免费吗？**
A: 公开仓库完全免费。私有仓库每月有免费额度（2000 分钟），通常足够使用。

**Q: 如果我的账户签到失败怎么办？**
A: 工作流会自动记录日志，你可以在 Actions 页面查看详细错误信息。

**Q: 可以更改执行频率吗？**
A: 可以，修改 cron 表达式即可。最短间隔为 5 分钟。

**Q: session 文件会保存吗？**
A: 会，但每次 GitHub Actions 运行都是全新的环境，session 会作为 artifact 保存。不过下次运行时还是会重新登录（因为无法从上次的 artifact 恢复）。
