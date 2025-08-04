from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys
import threading
from urllib.parse import urlparse
import mimetypes
import uuid
from datetime import datetime

# 添加项目路径到Python路径
project_path = os.path.dirname(os.path.abspath(__file__))
jmcomic_path = os.path.join(project_path, 'JMComic-Crawler-Python-master', 'src')
sys.path.insert(0, jmcomic_path)

# 确保下载目录存在
download_dir = os.path.join(project_path, 'downloads')
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 存储下载任务信息
download_tasks = {}

class JMComicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析请求路径
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 静态文件服务
        if path == '/':
            self.serve_file('index.html', 'text/html')
        elif path == '/style.css':
            self.serve_file('style.css', 'text/css')
        elif path == '/script.js':
            self.serve_file('script.js', 'application/javascript')
        elif path == '/favicon.ico':
            self.send_error(404)
        elif path == '/downloads':
            # 显示下载目录内容
            self.show_downloads()
        elif path.startswith('/download/'):
            # 提供下载文件服务
            self.serve_download_file(path[len('/download/'):])
        elif path == '/tasks':
            # 显示下载任务
            self.show_tasks()
        elif path == '/USER_GUIDE.md':
            # 提供用户指南
            self.serve_file('USER_GUIDE.md', 'text/markdown')
        elif path == '/CODESPACES_GUIDE.md':
            # 提供Codespaces使用指南
            self.serve_file('CODESPACES_GUIDE.md', 'text/markdown')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            comic_id = data.get('comic_id', [''])[0]
            
            if not comic_id:
                self.send_error(400, 'Missing comic_id')
                return
            
            # 创建任务ID
            task_id = str(uuid.uuid4())
            
            # 记录任务信息
            download_tasks[task_id] = {
                'comic_id': comic_id,
                'status': 'started',
                'timestamp': datetime.now().isoformat(),
                'message': '开始下载...'
            }
            
            # 异步执行下载任务
            thread = threading.Thread(target=self.start_download, args=(comic_id, task_id))
            thread.daemon = True
            thread.start()
            
            # 立即返回响应
            self.send_response(202)  # Accepted
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "accepted",
                "task_id": task_id,
                "message": f"开始下载漫画 {comic_id}，请稍后查看下载目录"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/downloads':
            # 获取下载列表
            self.get_downloads_list()
        elif self.path == '/api/tasks':
            # 获取任务列表
            self.get_tasks_list()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def start_download(self, comic_id, task_id):
        """
        在后台执行下载任务
        """
        try:
            # 更新任务状态
            download_tasks[task_id]['status'] = 'downloading'
            download_tasks[task_id]['message'] = '正在下载漫画...'
            
            # 导入JMComic
            import jmcomic
            
            # 创建配置
            option = jmcomic.JmOption.default()
            option.download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
            
            # 设置客户端配置
            option.retry_times = 3
            option.timeout = 30  # 增加超时时间
            
            # 执行下载
            jmcomic.download_album(comic_id, option)
            
            # 更新任务状态
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['message'] = f'漫画 {comic_id} 下载完成'
            download_tasks[task_id]['path'] = os.path.join('downloads', comic_id)
            
            print(f"漫画 {comic_id} 下载完成")
        except Exception as e:
            # 更新任务状态
            download_tasks[task_id]['status'] = 'failed'
            download_tasks[task_id]['message'] = f'下载失败: {str(e)}'
            print(f"下载漫画 {comic_id} 时出错: {str(e)}")

    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)

    def show_downloads(self):
        """
        显示下载目录内容
        """
        try:
            # 获取下载目录中的文件和文件夹
            items = os.listdir(download_dir)
            items.sort()
            
            # 生成HTML页面
            html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>下载目录</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }
        a { text-decoration: none; color: #007bff; }
        a:hover { text-decoration: underline; }
        .file { background-color: #e9f7ef; }
        .folder { background-color: #f8f9fa; }
        .back-link { margin-bottom: 20px; display: inline-block; }
    </style>
</head>
<body>
    <h1>已下载的漫画</h1>
    <a href="/" class="back-link">← 返回下载器</a>
'''
            
            if not items:
                html += '<p>暂无下载内容</p>'
            else:
                html += '<ul>'
                for item in items:
                    item_path = os.path.join(download_dir, item)
                    if os.path.isdir(item_path):
                        html += f'<li class="folder">📁 <a href="/download/{item}/">{item}/</a></li>'
                    else:
                        html += f'<li class="file">📄 <a href="/download/{item}">{item}</a></li>'
                html += '</ul>'
            
            html += '''
</body>
</html>
'''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"无法列出下载目录: {str(e)}")

    def show_tasks(self):
        """
        显示下载任务
        """
        try:
            # 生成HTML页面
            html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>下载任务</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .status-started { color: #007bff; }
        .status-downloading { color: #ffc107; }
        .status-completed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .back-link { margin-bottom: 20px; display: inline-block; }
    </style>
</head>
<body>
    <h1>下载任务</h1>
    <a href="/" class="back-link">← 返回下载器</a>
'''
            
            if not download_tasks:
                html += '<p>暂无下载任务</p>'
            else:
                html += '''
<table>
    <tr>
        <th>漫画ID</th>
        <th>状态</th>
        <th>时间</th>
        <th>消息</th>
    </tr>
'''
                # 按时间倒序排列任务
                sorted_tasks = sorted(download_tasks.items(), key=lambda x: x[1]['timestamp'], reverse=True)
                
                for task_id, task_info in sorted_tasks:
                    status_class = f"status-{task_info['status']}"
                    html += f'''
    <tr>
        <td>{task_info['comic_id']}</td>
        <td class="{status_class}">{task_info['status']}</td>
        <td>{task_info['timestamp'][:19].replace('T', ' ')}</td>
        <td>{task_info['message']}</td>
    </tr>
'''
                html += '</table>'
            
            html += '''
</body>
</html>
'''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"无法显示任务列表: {str(e)}")

    def serve_download_file(self, file_path):
        """
        提供下载文件服务
        """
        try:
            # 构建完整文件路径
            full_path = os.path.join(download_dir, file_path)
            
            # 安全检查，防止路径遍历攻击
            if not os.path.abspath(full_path).startswith(os.path.abspath(download_dir)):
                self.send_error(403, "访问被拒绝")
                return
            
            # 检查文件是否存在
            if not os.path.exists(full_path):
                self.send_error(404, "文件不存在")
                return
            
            # 如果是目录，显示目录内容
            if os.path.isdir(full_path):
                # 获取目录中的文件和文件夹
                items = os.listdir(full_path)
                items.sort()
                
                # 生成HTML页面
                html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{file_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
        a {{ text-decoration: none; color: #007bff; }}
        a:hover {{ text-decoration: underline; }}
        .file {{ background-color: #e9f7ef; }}
        .folder {{ background-color: #f8f9fa; }}
        .back-link {{ margin-bottom: 20px; display: inline-block; }}
    </style>
</head>
<body>
    <h1>目录: {file_path}</h1>
    <a href="/downloads" class="back-link">← 返回下载目录</a> | <a href="/" class="back-link">← 返回下载器</a>
'''
                
                if not items:
                    html += '<p>此目录为空</p>'
                else:
                    html += '<ul>'
                    # 添加返回上级目录的链接（如果不是根下载目录）
                    if file_path != "":
                        html += '<li class="folder">📁 <a href="../">../</a></li>'
                    
                    for item in items:
                        item_full_path = os.path.join(full_path, item)
                        relative_path = os.path.join(file_path, item).replace('\\', '/')
                        if os.path.isdir(item_full_path):
                            html += f'<li class="folder">📁 <a href="/download/{relative_path}/">{item}/</a></li>'
                        else:
                            html += f'<li class="file">📄 <a href="/download/{relative_path}">{item}</a></li>'
                    html += '</ul>'
                
                html += '''
</body>
</html>
'''
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                # 提供文件下载
                # 确定文件的MIME类型
                mime_type, _ = mimetypes.guess_type(full_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                # 读取并发送文件
                with open(full_path, 'rb') as file:
                    content = file.read()
                
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(full_path)}"')
                self.end_headers()
                self.wfile.write(content)
                
        except Exception as e:
            self.send_error(500, f"无法提供文件: {str(e)}")

    def get_downloads_list(self):
        """
        获取下载列表（API接口）
        """
        try:
            items = os.listdir(download_dir)
            items.sort()
            
            downloads = []
            for item in items:
                item_path = os.path.join(download_dir, item)
                if os.path.isdir(item_path):
                    downloads.append({
                        'name': item,
                        'type': 'folder',
                        'path': item
                    })
                else:
                    downloads.append({
                        'name': item,
                        'type': 'file',
                        'path': item
                    })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(downloads, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"无法获取下载列表: {str(e)}")

    def get_tasks_list(self):
        """
        获取任务列表（API接口）
        """
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(download_tasks, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"无法获取任务列表: {str(e)}")

def run_server(host='0.0.0.0', port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, JMComicHandler)
    print(f'JMComic 下载器服务器启动在 http://{host}:{port}')
    print('注意：所有用户共享同一个下载目录')
    httpd.serve_forever()

if __name__ == '__main__':
    # 可以通过命令行参数指定主机和端口
    import sys
    host = '0.0.0.0'  # 默认绑定到所有接口
    port = 8000       # 默认端口
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    run_server(host, port)