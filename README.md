# RecordAll 屏幕录制与回放工具

## 项目简介
RecordAll是一个基于Python的屏幕录制与回放工具，它能够自动捕获屏幕内容，并通过OCR技术识别屏幕中的文字，支持历史记录回放和文本搜索功能。

## 主要特性
- 自动屏幕捕获
- OCR文字识别
- 历史记录回放
- 文本内容搜索
- 图片缓存优化

## 技术栈
### 核心框架
- Python 3
- PyQt6：GUI框架
- SQLAlchemy：ORM框架
- SQLite：数据存储

### 图像处理
- OpenCV：屏幕捕获
- Pillow：图像处理
- WebP：图像压缩存储

### OCR引擎
- PaddleOCR：文字识别引擎

## 项目架构
### MVC架构
- Model：数据模型和业务逻辑
  - Database：数据库连接和表结构
  - ImageStore：图片存储和缓存管理
  - OCRStore：OCR结果管理

- View：用户界面
  - MainWindow：主窗口
  - ViewerWindow：图片查看窗口

- Service：业务服务
  - OCRService：OCR识别服务

### 性能优化
- LRU缓存：使用OrderedDict实现图片缓存
- WebP压缩：优化图片存储空间
- 异步处理：OCR识别异步执行

## 数据存储
### 图片存储
- 使用WebP格式压缩存储
- 支持LRU缓存机制

### 数据库设计
- images表：存储图片数据和时间戳
- ocr_texts表：存储OCR识别结果和位置信息

## 开发环境
- Python 3.8+
- pip install -r requirements.txt