# GLaDOS Auto Check-in

自动登录 GLaDOS VPN 服务并进行每日签到的 Python 脚本。

## 功能特性

- ✅ 自动发送验证码到邮箱
- ✅ 从 Gmail 自动读取验证码（支持两种邮件格式）
- ✅ 自动登录 GLaDOS
- ✅ 自动执行每日签到
- ✅ 保存登录会话，避免重复登录
- ✅ 支持 SOCKS5 代理连接 Gmail
- ✅ 配置文件管理，方便修改

## 环境要求

- Python 3.7+
- Anaconda（推荐）或 pip

## 安装步骤

### 1. 创建 Anaconda 虚拟环境

```bash
# 创建虚拟环境
conda create -n glados-checkin python=3.11

# 激活虚拟环境
conda activate glados-checkin
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 Gmail 应用密码

由于 Google 增强了安全性，需要使用应用专用密码：

1. 访问 https://myaccount.google.com/apppasswords
2. 登录你的 Google 账户
3. 选择"邮件"和"其他（自定义名称）"
4. 输入名称如"GLaDOS Check-in"
5. 点击"生成"，会得到一个 16 位密码
6. 将此密码复制到 `config.yaml` 的 `email.password` 字段

### 4. 配置 config.yaml

编辑 `config.yaml` 文件，设置你的邮箱和应用密码：

```yaml
email:
  address: "your_email@gmail.com"  # 你的 Gmail 地址
  password: "your_app_password"     # Gmail 应用专用密码
```

## 使用方法

### 运行程序

```bash
python3 glados_checkin.py
```

### 首次运行（需要登录）

程序会自动执行以下步骤：

1. 发送验证码到你的邮箱
2. 等待并读取 Gmail 中的验证码
3. 使用验证码登录 GLaDOS
4. 保存会话到 `session.json` 文件
5. 执行每日签到

### 后续运行（使用已保存的会话）

程序会直接使用已保存的会话：
1. 加载已保存的会话
2. 执行每日签到

### 运行输出示例

首次运行：
```
==================================================
GLaDOS Auto Check-in
==================================================

Step 1: Requesting verification code...
✓ Verification code sent to huichangshen02@gmail.com

Step 2: Waiting for verification code...
  (Check your Gmail inbox)
✓ Verification code found: 513544

Step 3: Logging in with code: 513544...
✓ Login successful
✓ Session saved to session.json

✓ Login process completed successfully!

Step 4: Performing daily check-in...
  Current points: {'email': 'user@gmail.com', 'points': 100}
✓ Check-in successful
  Response: {'message': 'Check-in successful', 'points': 105}
  User status: {'email': 'user@gmail.com', 'expire': 2024-12-31}

✓ All tasks completed successfully!
```

后续运行：
```
==================================================
GLaDOS Auto Check-in
==================================================
✓ Session loaded from session.json
✓ Using existing session (skip login)

Step 4: Performing daily check-in...
✓ Check-in successful

✓ All tasks completed successfully!
```

## 项目结构

```
auto-checkin/
├── config.yaml           # 配置文件
├── glados_checkin.py     # 主程序
├── requirements.txt      # Python 依赖
├── session.json          # 登录会话（自动生成）
└── README.md            # 说明文档
```

## 配置说明

`config.yaml` 文件包含以下配置项：

```yaml
# 邮箱设置
email:
  address: "your_email@gmail.com"      # Gmail 地址
  password: ""                          # Gmail 应用专用密码
  imap_server: "imap.gmail.com"         # IMAP 服务器
  imap_port: 993                        # IMAP 端口

# 代理设置（可选）
proxy:
  # SOCKS5 代理用于 IMAP 连接（如 Clash、v2ray 等）
  # 留空则禁用代理
  socks5_host: ""                       # 代理服务器地址，如 "192.168.1.237"
  socks5_port: 7891                     # SOCKS5 端口（Clash: 7891, v2ray: 1080）

# GLaDOS 设置
glados:
  base_url: "https://glados.cloud"        # GLaDOS 网站
  login_url: "https://glados.cloud/api/login"        # 登录 API
  auth_url: "https://glados.cloud/api/authorization" # 授权 API
  site: "glados.network"                # 站点标识

# 会话设置
session:
  save_path: "session.json"             # 会话保存路径
```

## 注意事项

1. **Gmail 安全性**：
   - 必须使用应用专用密码，不能使用账户密码
   - 确保 Gmail 已开启 IMAP 访问权限
   - 访问 https://mail.google.com/mail/u/0/#settings/fwdandpop 确认 IMAP 已启用

2. **代理配置**：
   - 如果无法连接到 Gmail，可配置 SOCKS5 代理
   - 确保代理工具（如 Clash、v2ray）正在运行
   - 查看代理工具配置确认 SOCKS5 端口

3. **会话管理**：
   - 登录成功后会保存会话到 `session.json`
   - 下次运行时会优先使用已保存的会话
   - 如需重新登录，删除 `session.json` 文件

4. **每日签到**：
   - 程序会在登录后自动执行签到
   - 签到会显示当前积分和用户状态
   - 建议配合定时任务（如 cron）每天自动运行

5. **验证码等待时间**：
   - 默认等待 60 秒接收验证码
   - 每 2 秒检查一次邮箱

## 定时任务设置

### 方式一：GitHub Actions（推荐）✨

使用 GitHub Actions 可以实现云端自动签到，无需本地运行。

**优势**：
- ✅ 无需本地运行，24/7 在线
- ✅ 完全免费（公开仓库）
- ✅ 自动重试失败
- ✅ 查看执行日志
- ✅ 支持手动触发

**快速开始**：

1. 将代码推送到 GitHub
2. 在仓库设置中添加 Secrets（邮箱地址和密码）
3. 每天早上 8 点自动执行签到

**详细配置指南**：查看 [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)

### 方式二：Linux (crontab)

```bash
# 编辑 crontab
crontab -e

# 添加每天早上 9 点执行签到
0 9 * * * cd /path/to/auto-checkin && /path/to/anaconda3/envs/glados-checkin/bin/python glados_checkin.py >> checkin.log 2>&1
```

### 方式三：Windows (Task Scheduler)

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天固定时间）
4. 设置操作：运行 `python3 glados_checkin.py`
5. 设置起始目录为项目路径

## 后续开发

当前实现的功能：
- ✅ 发送验证码
- ✅ 读取 Gmail 验证码
- ✅ 登录功能
- ✅ 会话管理
- ✅ 每日签到
- ✅ 代理支持
- ✅ Session 过期自动重新登录
- ✅ GitHub Actions 定时任务

可选的增强功能：
- 日志记录
- 邮件通知签到结果
- 多账号支持
- Telegram/微信通知

## 故障排除

### 问题：无法连接到 Gmail

**解决方案**：
1. 确认已开启 IMAP：https://mail.google.com/mail/u/0/#settings/fwdandpop
2. 确认使用应用专用密码而非账户密码
3. 如果需要代理访问，配置 `config.yaml` 中的代理设置
4. 检查防火墙设置

### 问题：未收到验证码

**解决方案**：
1. 检查垃圾邮件文件夹
2. 确认邮箱地址正确
3. 等待更长时间（默认 60 秒）

### 问题：登录失败

**解决方案**：
1. 确认验证码正确（注意：程序会选择最新的邮件中的验证码）
2. 检查网络连接
3. 查看错误信息详情

### 问题：签到失败

**解决方案**：
1. 确认会话有效（删除 `session.json` 重新登录）
2. 检查网络连接
3. 查看错误信息详情