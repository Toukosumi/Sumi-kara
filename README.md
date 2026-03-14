# Sumi-Kara

墨卡拉 (Sumi-Kara) - 一款基于 Python PyQt5 的桌面多功能工具集。

## 功能模块

| 模块 | 描述 |
|------|------|
| 视频下载器 | 支持多平台视频下载 (yt-dlp) |
| 歌词下载器 | 歌曲歌词获取 |
| 歌词合并器 | 歌词文件合并处理 |
| 设置 | 应用配置管理 |

## 技术栈

- **GUI 框架**: PyQt5
- **打包工具**: PyInstaller
- **外部工具**: FFmpeg, yt-dlp

## 环境要求

- Python 3.10+
- Windows 10/11

## 安装

```bash
# 1. 创建虚拟环境 (可选)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 构建 exe

```bash
pyinstaller build.spec --noconfirm
```

构建完成后，可执行文件位于 `dist/Sumi-Kara.exe`

## 项目结构

```
Sumi-Kara/
├── main.py              # 入口文件
├── app.py               # Qt 应用创建
├── config/              # 配置文件
├── modules/             # 功能模块
│   ├── base/            # 模块基类
│   └── impl/            # 模块实现
├── ui/                  # UI 组件
│   ├── main_window.py   # 主窗口
│   └── widgets/         # 自定义组件
└── utils/               # 工具函数
```

## 许可证

MIT License
