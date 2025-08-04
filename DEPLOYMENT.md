# JMComic 下载器部署指南

本文档将指导您如何将JMComic下载器部署到个人网站或云服务器上。

## 部署选项

### 1. 使用云服务器 (推荐)

#### 选择云服务提供商
- **DigitalOcean** - 简单易用，价格合理
- **Linode** - 性能良好，价格实惠
- **AWS EC2** - 功能丰富，可免费试用
- **阿里云/腾讯云** - 国内访问速度快

#### 部署步骤

1. **准备服务器**
   - 选择一个Linux发行版（如Ubuntu 20.04）
   - 确保至少有1GB内存和20GB存储空间
   - 开放端口8000（或您选择的端口）

2. **安装依赖**
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   
   # 安装Python 3和pip
   sudo apt install python3 python3-pip -y
   
   # 安装Git（如果需要从GitHub克隆）
   sudo apt install git -y
   ```

3. **上传项目文件**
   可以通过以下方式之一上传文件：
   
   方式一：使用Git克隆
   ```bash
   git clone https://github.com/your-username/your-repo.git
   ```
   
   方式二：使用SCP命令
   ```bash
   scp -r /path/to/JMdownloader2 user@your-server-ip:/home/user/
   ```

4. **安装Python依赖**
   ```bash
   cd JMdownloader2
   pip3 install -r requirements.txt
   ```

5. **运行应用**
   ```bash
   python3 app.py 0.0.0.0 8000
   ```

6. **设置后台运行**
   使用systemd创建服务：
   
   创建服务文件：
   ```bash
   sudo nano /etc/systemd/system/jmcomic.service
   ```
   
   添加以下内容：
   ```ini
   [Unit]
   Description=JMComic Downloader
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/path/to/JMdownloader2
   ExecStart=/usr/bin/python3 /path/to/JMdownloader2/app.py 0.0.0.0 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   
   启用并启动服务：
   ```bash
   sudo systemctl enable jmcomic.service
   sudo systemctl start jmcomic.service
   ```

### 2. 使用应用平台

#### Heroku (免费额度)
1. 创建[Heroku](https://heroku.com/)账户
2. 安装[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. 在项目目录中创建[Procfile](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/Procfile)文件：
   ```
   web: python app.py 0.0.0.0 $PORT
   ```
4. 创建[requirements.txt](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/requirements.txt)文件（已创建）
5. 部署：
   ```bash
   heroku create
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku master
   ```

#### PythonAnywhere
1. 创建[PythonAnywhere](https://www.pythonanywhere.com/)账户
2. 上传项目文件
3. 创建Web应用并配置WSGI文件
4. 安装依赖

### 3. 使用容器化部署

#### Docker部署
1. 创建Dockerfile：
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["python", "app.py", "0.0.0.0", "8000"]
   ```

2. 构建并运行容器：
   ```bash
   docker build -t jmcomic-downloader .
   docker run -p 8000:8000 jmcomic-downloader
   ```

## 安全注意事项

### 1. 访问控制
默认情况下，任何人都可以使用您的下载器。为防止滥用，建议添加以下安全措施：

1. **添加基本认证**
   在[app.py](file:///c%3A/Users/mj102/Desktop/%E4%B8%8B%E8%BD%BD/JMdownloader2/app.py)中添加认证逻辑：
   ```python
   import base64
   
   def check_auth(self):
       auth_header = self.headers.get('Authorization')
       if not auth_header:
           return False
       
       try:
           auth_type, credentials = auth_header.split(' ', 1)
           if auth_type.lower() != 'basic':
               return False
           
           username, password = base64.b64decode(credentials).decode().split(':', 1)
           # 在这里验证用户名和密码
           return username == 'admin' and password == 'your-password'
       except:
           return False
   ```

2. **使用反向代理**
   使用Nginx或Apache作为反向代理，并配置访问控制。

### 2. 资源限制
为防止资源耗尽，建议：

1. **限制并发下载数**
2. **设置下载速度限制**
3. **定期清理旧的下载文件**

### 3. 日志记录
启用详细的日志记录以监控使用情况：
```python
import logging

logging.basicConfig(
    filename='jmcomic.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 性能优化

### 1. 使用反向代理
使用Nginx作为反向代理可以提高性能和安全性：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 启用HTTPS
使用Let's Encrypt获取免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 故障排除

### 常见问题

1. **无法访问网站**
   - 检查防火墙设置
   - 确认端口已正确开放
   - 检查服务器安全组设置

2. **下载失败**
   - 检查服务器网络连接
   - 确认目标网站可访问
   - 检查是否触发反爬机制

3. **内存不足**
   - 增加服务器内存
   - 限制并发下载数量
   - 定期清理下载文件

### 监控和维护

1. **检查服务状态**
   ```bash
   systemctl status jmcomic.service
   ```

2. **查看日志**
   ```bash
   journalctl -u jmcomic.service -f
   ```

3. **定期更新**
   定期更新JMComic库以获取最新功能和修复：
   ```bash
   pip3 install --upgrade jmcomic
   ```

## 法律和道德考虑

在部署和使用此下载器时，请注意：

1. **遵守当地法律法规**
2. **尊重网站服务条款**
3. **适度使用，避免对目标网站造成过大压力**
4. **仅下载用于个人学习和收藏的内容**
5. **不要分发受版权保护的材料**

通过遵循这些指南，您可以成功将JMComic下载器部署到个人网站上，并安全、有效地使用它。