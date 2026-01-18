# 本地定时任务部署指南

本指南说明如何在本地配置定时任务，实现每天中午 12 点（北京时间）自动执行签到。

## 已配置的内容

### 1. 启动脚本：`run_checkin.sh`

- 自动切换到项目目录
- 激活 conda 环境
- 执行签到脚本
- 记录日志到 `checkin_YYYYMMDD.log`

### 2. Crontab 定时任务

```bash
# 查看当前的 crontab 配置
crontab -l
```

**当前配置**：
- 执行时间：每天中午 12 点（北京时间）
- UTC 时间：凌晨 4 点
- Cron 表达式：`0 4 * * *`

## 使用方法

### 手动测试脚本

```bash
# 在项目目录下执行
bash run_checkin.sh
```

### 查看 crontab 配置

```bash
crontab -l
```

### 编辑 crontab

```bash
crontab -e
```

### 查看日志

```bash
# 今天的日志
cat checkin_$(date +%Y%m%d).log

# 所有日志文件
ls -lh checkin_*.log
```

## 修改执行时间

如果想要修改执行时间，编辑 crontab：

```bash
crontab -e
```

### 修改时间示例

| 北京时间 | UTC 时间 | Cron 表达式 |
|---------|---------|-------------|
| 中午 12 点 | 凌晨 4 点 | `0 4 * * *` |
| 早上 8 点 | 凌晨 0 点 | `0 0 * * *` |
| 早上 9 点 | 凌晨 1 点 | `0 1 * * *` |
| 晚上 8 点 | 中午 12 点 | `0 12 * * *` |
| 每小时执行一次 | - | `0 * * * *` |

### 修改步骤

1. 编辑 crontab：`crontab -e`
2. 修改时间表达式
3. 保存退出（编辑器操作）

## 日志管理

### 日志文件位置

日志文件保存在项目目录下：
- 文件名格式：`checkin_YYYYMMDD.log`
- 例如：`checkin_20250118.log`

### 自动清理旧日志

可以创建一个清理脚本 `clean_logs.sh`：

```bash
#!/bin/bash
# Delete logs older than 30 days
find . -name "checkin_*.log" -mtime +30 -delete
echo "Old logs cleaned at $(date)"
```

添加到 crontab 每周清理一次：

```bash
# 每周日凌晨 3 点清理日志
0 3 * * 0 find /home/shen/Work/CodeSpace/Python/auto-checkin -name "checkin_*.log" -mtime +30 -delete
```

## 验证配置

### 1. 查看 crontab 是否正确安装

```bash
crontab -l
```

应该看到：
```
# GLaDOS Auto Check-in - Daily at 12 PM Beijing Time (4 AM UTC)
0 4 * * * bash run_checkin.sh
```

### 2. 查看 cron 服务状态

```bash
# Linux 系统
sudo systemctl status cron
# 或
sudo service cron status
```

### 3. 查看 cron 日志

```bash
# 查看系统 cron 日志
sudo grep CRON /var/log/syslog | tail -20
```

### 4. 测试脚本

手动运行一次脚本，确认能正常工作：

```bash
bash run_checkin.sh
```

## 常见问题

### Q: 定时任务没有执行？

**检查清单**：

1. 确认 cron 服务正在运行
```bash
sudo systemctl status cron
```

2. 查看 cron 日志
```bash
sudo grep CRON /var/log/syslog | tail -20
```

3. 检查脚本权限
```bash
ls -lh run_checkin.sh
# 应该有可执行权限 (rwxr-xr-x)
```

4. 手动运行脚本，确认脚本能正常工作
```bash
bash run_checkin.sh
```

5. 检查 crontab 语法
```bash
crontab -l
```

### Q: 脚本运行但签到失败？

**解决方案**：

1. 查看日志文件
```bash
cat checkin_$(date +%Y%m%d).log
```

2. 检查 conda 环境路径
```bash
which conda
conda env list
```

3. 检查 config.yaml 是否存在
```bash
ls -la config.yaml
```

### Q: 如何临时禁用定时任务？

编辑 crontab，在任务前加 `#` 注释掉：

```bash
crontab -e
# 修改为：
# 0 4 * * * bash run_checkin.sh
```

### Q: 如何立即测试定时任务？

不等待定时执行，直接运行脚本：

```bash
bash run_checkin.sh
```

## 卸载定时任务

如果不再需要自动签到，删除 crontab：

```bash
crontab -r
```

## 系统兼容性

本配置适用于：
- ✅ Ubuntu/Debian
- ✅ CentOS/RHEL
- ✅ macOS
- ✅ 其他 Linux 发行版

## 注意事项

1. **确保系统时间正确**
   - 定时任务依赖系统时间
   - 使用 `date` 命令检查当前时间

2. **确保系统在运行**
   - 定时任务只在系统运行时执行
   - 如果电脑休眠或关机，任务不会执行

3. **定期检查日志**
   - 查看签到是否成功
   - 及时发现问题

4. **保持脚本更新**
   - 从 GitHub 拉取最新代码
   - 确保功能正常
