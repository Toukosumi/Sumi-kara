# GitHub 仓库创建与推送指南

## 步骤 1: 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com/) 并登录你的账号
2. 点击右上角 **+** 按钮，选择 **New repository**
3. 填写以下信息：
   - **Repository name**: `Sumi-Kara` (或你喜欢的名称)
   - **Description**: 多功能视频制作软件
   - **Visibility**: 选择 **Public** (公开) 或 **Private** (私有)
   - **不要勾选** "Add a README file"
   - **不要勾选** "Add .gitignore"
   - **不要勾选** "Choose a license"
4. 点击 **Create repository**

## 步骤 2: 关联远程仓库

创建完成后，GitHub 会显示仓库地址。在项目中执行以下命令：

```bash
cd "D:\Project\PythonProject\Sumi-Kara"

# 关联远程仓库 (替换 <your-username> 为你的 GitHub 用户名)
git remote add origin https://github.com/<your-username>/Sumi-Kara.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git push -u origin master
```

## 步骤 3: 使用 SSH (可选)

如果你使用 SSH 密钥认证：

```bash
# 关联 SSH 地址
git remote add origin git@github.com:<your-username>/Sumi-Kara.git

# 推送
git push -u origin master
```

## 常见问题

### Q: 提示 `remote origin already exists`
```bash
# 删除原有远程仓库
git remote remove origin

# 重新添加
git remote add origin <新的仓库地址>
```

### Q: 推送失败，提示分支不匹配
```bash
# 如果 GitHub 默认创建的是 main 分支
git branch -M master
git push -u origin master
```

### Q: 需要输入 GitHub 账号密码
- GitHub 已停用密码验证，需使用 **Personal Access Token**
- 访问：Settings → Developer settings → Personal access tokens → Generate new token
- 勾选 `repo` 权限，生成后复制 Token
- 推送时用户名输入你的 GitHub 用户名，密码粘贴 Token
