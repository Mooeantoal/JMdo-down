# JMComic 网页下载器

这是一个基于 Web 的 JMComic 下载器界面，允许用户通过网页界面下载禁漫天堂的漫画。

## 功能特点

- 简洁直观的用户界面
- 实时下载进度显示
- 错误处理和重试机制
- 基于 Python 的后端服务
- 集成真实的 JMComic-Crawler-Python 项目

## 安装和运行

### 方法一：使用现有的 JMComic 库

1. 确保已安装 Python 3.7+
2. 安装 JMComic 库：
   ```bash
   pip install jmcomic -i https://pypi.org/project -U
   ```
3. 在项目目录中运行以下命令启动服务器：
   ```bash
   python server.py
   ```
4. 打开浏览器访问 `http://localhost:8000`

### 方法二：使用本地的 JMComic-Crawler-Python 项目

1. 确保 [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) 项目位于 `JMComic-Crawler-Python-master` 目录中
2. 在项目目录中运行以下命令启动服务器：
   ```bash
   python server.py
   ```
3. 打开浏览器访问 `http://localhost:8000`

## 使用方法

1. 在输入框中输入漫画 ID（例如：422866）
2. 点击"下载"按钮开始下载
3. 等待下载完成（可以查看进度条）
4. 下载完成后可以在 `downloads` 目录中找到下载的漫画

## 下载目录位置说明

下载的漫画文件保存位置取决于您运行应用程序的方式：

### 本地运行
当您在本地计算机上运行应用程序时，下载的文件会保存在项目目录中的 `downloads` 文件夹内。

### 服务器/Codespaces运行
当您在服务器或Codespaces等远程环境中运行应用程序时，下载的文件会保存在远程环境的文件系统中。

您可以通过以下方式访问下载的文件：
1. 点击网页界面上的"查看已下载内容"链接
2. 直接浏览服务器文件系统（如果您有访问权限）
3. 在Codespaces中通过文件浏览器下载文件到本地

## 多用户使用说明

当多个用户使用同一个下载器实例时，请参阅 [MULTIUSER_GUIDE.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/MULTIUSER_GUIDE.md) 文件了解详细信息。

## 在Codespaces中部署和共享

如果您希望在GitHub Codespaces中部署此应用程序并与他人共享，请参阅 [CODESPACES_GUIDE.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/CODESPACES_GUIDE.md) 文件了解详细说明。

## 部署到PythonAnywhere

如果您希望将此应用程序部署到PythonAnywhere免费托管服务，请参阅 [PYTHONANYWHERE_DEPLOY.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/PYTHONANYWHERE_DEPLOY.md) 文件了解详细说明。

## 部署到ByetHost

如果您希望将此应用程序部署到ByetHost免费或付费托管服务，请参阅 [BYETHOST_DEPLOY.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/BYETHOST_DEPLOY.md) 文件了解详细说明。

## 项目结构

```
JMdownloader2/
├── index.html              # 主页面
├── style.css               # 样式文件
├── script.js               # 前端交互逻辑
├── server.py               # 后端服务（包含下载逻辑）
├── JMComic-Crawler-Python-master/  # JMComic 项目源码
│   └── src/
│       └── jmcomic/        # JMComic Python 包
└── README.md               # 说明文档
```

## 技术实现

### 前端
- 使用原生 HTML/CSS/JavaScript 构建
- 响应式设计，适配不同屏幕尺寸
- AJAX 与后端通信

### 后端
- Python 内置 HTTP 服务器
- 集成 JMComic 库实现真实下载功能
- 支持错误处理和异常捕获

### 下载功能
- 使用 JMComic-Crawler-Python 项目作为核心下载库
- 支持单个漫画下载
- 自动处理图片解码和保存

## 网络问题解决方案

由于 JMComic 需要连接到特定网站来获取漫画信息，可能会遇到网络问题。以下是常见问题及解决方案：

### 1. 连接超时/网络错误

**解决方案：**
- 检查网络连接是否正常
- 尝试使用代理服务器
- 更换网络环境（如使用手机热点）

### 2. 反爬机制

**解决方案：**
- 避免频繁请求（增加请求间隔时间）
- 使用不同的用户代理
- 减少并发请求数量

### 3. 配置代理

JMComic 支持通过代码配置代理。如果需要使用代理，可以修改 [server.py](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/server.py) 中的 `download_with_jmcomic` 函数：

```python
def download_with_jmcomic(self, comic_id):
    try:
        import jmcomic
        
        # 创建默认配置
        option = jmcomic.JmOption.default()
        
        # 设置下载目录
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        option.download_dir = download_dir
        
        # 配置代理（如果需要）
        # option.headers = {
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        # }
        # option.proxy = 'http://127.0.0.1:1080'  # 替换为实际代理地址
        
        # 设置客户端配置以提高稳定性
        option.retry_times = 3
        option.timeout = 15
        
        # 实际下载漫画
        album = jmcomic.download_album(comic_id, option)
        
        return {
            "status": "success",
            "message": f"漫画 {comic_id} 下载完成",
            "path": os.path.join(download_dir, str(comic_id))
        }
    except Exception as e:
        # 错误处理代码...
```

### 4. 使用配置文件

你也可以创建一个配置文件来设置代理和其他选项：

1. 创建 `option.yml` 文件：
```yaml
client:
  impl: html
  domain: 
    - jmcomic.me
  headers:
    user-agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  proxy: "http://127.0.0.1:1080"  # 如果需要代理，替换为实际代理地址

download:
  delay:
    per_page: 0.5  # 每页下载间隔0.5秒
```

2. 修改代码使用配置文件：
```python
option = jmcomic.create_option_by_file('option.yml')
album = jmcomic.download_album(comic_id, option)
```

## 部署到个人网站

有关如何将此应用程序部署到个人网站或云服务器的详细说明，请参阅 [DEPLOYMENT.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/DEPLOYMENT.md) 文件。

## 在GitHub生态系统中使用

虽然不能直接将完整的JMComic下载器部署到GitHub Pages（因为它是静态托管服务，无法运行后端Python代码），但您可以使用其他方式在GitHub生态系统中使用此工具。详细信息请参阅 [GITHUB_PAGES.md](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/GITHUB_PAGES.md) 文件。

## 常见问题排查

### 1. 无法启动服务器
- 确保已安装 Python 3.7+
- 确保 JMComic 库已正确安装，或 JMComic-Crawler-Python-master 目录存在

### 2. 下载失败
- 检查网络连接
- 确认提供的漫画 ID 是否正确
- 检查是否触发了网站的反爬机制

### 3. 无法找到模块
- 确保 JMComic-Crawler-Python-master 目录结构正确
- 确保 src 目录中包含 jmcomic 包

## 注意事项

- 请遵守网站使用条款，不要过度频繁地请求
- 下载的漫画仅供个人学习和收藏使用
- 建议在生产环境中添加适当的安全措施和错误处理
- 根据网络情况，下载可能需要一些时间

## 扩展功能建议

1. 添加下载历史记录功能
2. 支持暂停/继续下载
3. 添加配置选项（下载路径、图片质量等）
4. 支持搜索漫画功能
5. 添加用户认证系统
6. 实现下载速度控制
7. 添加多线程下载支持