# 视频下载模块实现进度

## 任务列表

- [x] 1. 修改 main_window.py - 使用模块的 get_config_widget()
- [x] 2. 创建 VideoDownloadWorker - 下载工作线程
- [x] 3. 修改 VideoDownloaderModule - 实现完整模块类
- [x] 4. 创建 VideoDownloaderConfigWidget - 配置界面
- [x] 5. 添加代理配置功能 (VideoDownloadWorker._should_use_proxy)

## 实现细节

### 关键函数说明

#### VideoDownloadWorker
- `run()`: 主线程函数，启动 QProcess 执行 yt-dlp
- `_build_arguments()`: 构建 yt-dlp 命令行参数，包含代理判断逻辑
- `_should_use_proxy(url)`: 判断 URL 是否需要走代理（YouTube 域名）
- `_handle_output()`: 解析 yt-dlp 输出，更新进度
- `stop()`: 停止下载，终止进程

#### VideoDownloaderModule
- `execute(params)`: 启动下载任务
- `get_config_widget()`: 返回配置界面
- `get_progress()`: 获取当前下载进度
- `stop()`: 停止当前下载

#### VideoDownloaderConfigWidget
- `_init_ui()`: 初始化界面组件
- `_load_config()`: 加载保存的配置
- `_on_download_clicked()`: 处理下载按钮点击
- `_on_progress_updated()`: 更新进度显示

### 配置项
- `video_download_path`: 下载保存路径
- `video_download_format`: 视频格式
- `video_proxy_enabled`: 代理是否启用
- `video_proxy_url`: 代理地址
- `yt_dlp_path`: yt-dlp.exe 路径
- `ffmpeg_path`: ffmpeg.exe 路径

### 文件路径
- yt-dlp.exe: `D:\Learning\Subtitles\FFmpeg\bin\yt-dlp.exe`
- ffmpeg.exe: `D:\Learning\Subtitles\FFmpeg\bin\ffmpeg.exe`

---

## 架构改进任务

### 优先级：高

#### 配置系统重构

- [x] 1. 创建模块级配置类 `VideoDownloaderConfig`
  - 将硬编码的默认值移至配置类中统一管理
  - 文件位置：`modules/impl/video_downloader_config.py`（新建）
  - 路径：`modules/impl/video_downloader.py` 中的 `DEFAULT_YT_DLP_PATH`、`DEFAULT_FFMPEG_PATH` 等

- [x] 2. 重构 `GlobalConfig` 类支持默认值定义
  - 改进 `config/global_config.py` 的 `DEFAULT_CONFIG` 字典
  - 支持模块级配置分组

- [x] 3. 移除 `VideoDownloaderModule._init_default_config()` 中的硬编码
  - 改用模块级配置类
  - 文件：`modules/impl/video_downloader.py`

#### 依赖注入改造

- [ ] 4. 为 `ModuleBase` 添加配置注入接口
  - 在 `modules/base/module_base.py` 添加 `set_config()` 方法
  - 降低模块与全局配置的耦合

- [ ] 5. 改造 `ModuleManager` 支持依赖注入
  - 在 `modules/manager.py` 中支持模块初始化时传入配置

### 优先级：中

#### 代码质量提升

- [x] 6. 为核心函数添加完整的类型注解
  - `modules/impl/video_downloader.py`
  - `modules/base/module_base.py`
  - `modules/manager.py`

- [ ] 7. 添加异常处理包装
  - 网络请求、文件操作添加 try-except
  - 添加错误恢复机制

#### 日志系统增强

- [x] 8. 添加日志轮转 (RotatingFileHandler)
  - 文件：`utils/__init__.py`
  - 避免日志文件无限增长

- [ ] 9. 添加日志分类配置
  - 区分 UI 日志、业务日志、网络日志

### 优先级：低

#### 测试与构建

- [ ] 10. 创建测试目录 `tests/`
  - 添加 `tests/test_module_base.py`
  - 添加 `tests/test_config.py`

- [ ] 11. 添加 `pytest.ini` 配置文件

- [ ] 12. 完善 `requirements.txt` 添加版本锁定
  - 使用 `pip-compile` 生成锁定版本

#### 文档

- [ ] 13. 添加模块开发指南 (DEVELOPMENT.md)
- [ ] 14. 完善 README.md 包含功能说明和使用方法
