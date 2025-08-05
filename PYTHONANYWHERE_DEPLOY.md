import json
import urllib.parse
import os
import threading
from urllib.parse import urlparse
import mimetypes
import uuid
from datetime import datetime

# 添加项目路径到Python路径
project_path = os.path.dirname(os.path.abspath(__file__))
jmcomic_path = os.path.join(project_path, 'JMComic-Crawler-Python-master', 'src')

# 确保下载目录存在
download_dir = os.path.join(project_path, 'downloads')
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 存储下载任务信息
download_tasks = {}

def application(environ, start_response):
    # 解析请求路径和方法
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # 处理静态文件
    if path == '/':
        return serve_static_file(environ, start_response, 'index.html', 'text/html')
    elif path == '/style.css':
        return serve_static_file(environ, start_response, 'style.css', 'text/css')
    elif path == '/script.js':
        return serve_static_file(environ, start_response, 'script.js', 'application/javascript')
    elif path == '/USER_GUIDE.md':
        return serve_static_file(environ, start_response, 'USER_GUIDE.md', 'text/markdown')
    elif path == '/CODESPACES_GUIDE.md':
        return serve_static_file(environ, start_response, 'CODESPACES_GUIDE.md', 'text/markdown')
    elif path == '/MULTIUSER_GUIDE.md':
        return serve_static_file(environ, start_response, 'MULTIUSER_GUIDE.md', 'text/markdown')
    elif path == '/favicon.ico':
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']
    elif path == '/downloads':
        # 显示下载目录内容
        return show_downloads(environ, start_response)
    elif path.startswith('/download/'):
        # 提供下载文件服务
        return serve_download_file(environ, start_response, path[len('/download/'):])
    elif path == '/tasks':
        # 显示下载任务
        return show_tasks(environ, start_response)
    elif path == '/api/download' and method == 'POST':
        return handle_download(environ, start_response)
    elif path == '/api/downloads' and method == 'GET':
        return get_downloads_list(environ, start_response)
    elif path == '/api/tasks' and method == 'GET':
        return get_tasks_list(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>404 Not Found</h1>']

def serve_static_file(environ, start_response, filename, content_type):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        start_response('200 OK', [
            ('Content-Type', content_type),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [content.encode('utf-8')]
    except FileNotFoundError:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>404 Not Found</h1>']

def handle_download(environ, start_response):
    try:
        # 获取POST数据
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length)
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        
        comic_id = data.get('comic_id', [''])[0]
        
        if not comic_id:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'status': 'error', 'message': 'Missing comic_id'}).encode('utf-8')]
        
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
        thread = threading.Thread(target=start_download, args=(comic_id, task_id))
        thread.daemon = True
        thread.start()
        
        # 立即返回响应
        response = {
            "status": "accepted",
            "task_id": task_id,
            "message": f"开始下载漫画 {comic_id}，请稍后查看下载目录"
        }
        
        start_response('202 Accepted', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps(response, ensure_ascii=False).encode('utf-8')]
        
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8')]

def start_download(comic_id, task_id):
    """
    在后台执行下载任务
    """
    try:
        # 更新任务状态
        download_tasks[task_id]['status'] = 'downloading'
        download_tasks[task_id]['message'] = '正在下载漫画...'
        
        # 导入JMComic
        try:
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
        except ImportError:
            # 模拟下载
            import time
            import json
            import os
            
            # 创建下载目录
            download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            
            # 创建漫画目录
            comic_dir = os.path.join(download_dir, comic_id)
            if not os.path.exists(comic_dir):
                os.makedirs(comic_dir)
            
            # 模拟下载时间
            time.sleep(2)
            
            # 创建模拟数据
            comic_info = {
                "id": comic_id,
                "title": f"漫画标题 {comic_id}",
                "author": "作者名称",
                "tags": ["标签1", "标签2"],
                "chapters": [
                    {"id": f"{comic_id}_001", "title": "第一章"},
                    {"id": f"{comic_id}_002", "title": "第二章"}
                ]
            }
            
            # 保存漫画信息
            info_file = os.path.join(comic_dir, "info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(comic_info, f, ensure_ascii=False, indent=2)
            
            # 更新任务状态
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['message'] = f'漫画 {comic_id} 下载完成（模拟）'
            download_tasks[task_id]['path'] = os.path.join('downloads', comic_id)
            
    except Exception as e:
        # 更新任务状态
        download_tasks[task_id]['status'] = 'failed'
        download_tasks[task_id]['message'] = f'下载失败: {str(e)}'
        print(f"下载漫画 {comic_id} 时出错: {str(e)}")

def show_downloads(environ, start_response):
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
        
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [html.encode('utf-8')]
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [f"无法列出下载目录: {str(e)}".encode('utf-8')]

def show_tasks(environ, start_response):
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
        
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [html.encode('utf-8')]
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [f"无法显示任务列表: {str(e)}".encode('utf-8')]

def serve_download_file(environ, start_response, file_path):
    """
    提供下载文件服务
    """
    try:
        # 构建完整文件路径
        full_path = os.path.join(download_dir, file_path)
        
        # 安全检查，防止路径遍历攻击
        if not os.path.abspath(full_path).startswith(os.path.abspath(download_dir)):
            start_response('403 Forbidden', [('Content-Type', 'text/plain')])
            return [b'Access denied']
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'File not found']
        
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
            
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html.encode('utf-8')]
        else:
            # 提供文件下载
            # 确定文件的MIME类型
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 读取并发送文件
            with open(full_path, 'rb') as file:
                content = file.read()
            
            start_response('200 OK', [
                ('Content-Type', mime_type),
                ('Content-Disposition', f'attachment; filename="{os.path.basename(full_path)}"')
            ])
            return [content]
            
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [f"无法提供文件: {str(e)}".encode('utf-8')]

def get_downloads_list(environ, start_response):
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
        
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps(downloads, ensure_ascii=False).encode('utf-8')]
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({'error': str(e)}).encode('utf-8')]

def get_tasks_list(environ, start_response):
    """
    获取任务列表（API接口）
    """
    try:
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps(download_tasks, ensure_ascii=False).encode('utf-8')]
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({'error': str(e)}).encode('utf-8')]