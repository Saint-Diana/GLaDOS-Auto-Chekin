# GitHub Actions 快速设置指南

## 5 分钟快速配置

### 第一步：添加 Secrets（2 分钟）

1. 打开你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

添加以下 secrets：

| Secret 名称 | 值 |
|------------|-----|
| `EMAIL_ADDRESS` | 你的 Gmail 地址（如：`user@gmail.com`）|
| `EMAIL_PASSWORD` | Gmail 应用专用密码（16位密码）|

如果你使用代理，还需要添加：

| Secret 名称 | 值 |
|------------|-----|
| `PROXY_HOST` | 代理服务器地址（如：`192.168.1.237`）|
| `PROXY_PORT` | 代理端口（如：`7898`）|

### 第二步：推送代码（1 分钟）

```bash
git add .
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### 第三步：验证配置（2 分钟）

1. 在 GitHub 仓库页面点击 **Actions** 标签
2. 点击左侧的 "GLaDOS Daily Check-in"
3. 点击 **Run workflow** 按钮
4. 点击绿色的 **Run workflow** 按钮进行手动测试

### 完成！

✅ 现在每天早上 8 点（北京时间）会自动执行签到

## 查看结果

- 在 **Actions** 页面可以看到所有执行记录
- 点击具体的运行记录可以查看详细日志
- 签到成功会显示 ✓

## 常见问题

**Q: Secrets 配置在哪里？**
A: 仓库 → Settings → Secrets and variables → Actions

**Q: 如何获取 Gmail 应用密码？**
A: https://myaccount.google.com/apppasswords

**Q: 如何修改执行时间？**
A: 编辑 `.github/workflows/daily-checkin.yml` 中的 cron 表达式

**Q: GitHub Actions 收费吗？**
A: 公开仓库完全免费

## 需要帮助？

查看详细配置指南：[GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)
