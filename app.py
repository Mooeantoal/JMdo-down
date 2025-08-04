from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys
import threading
from urllib.parse import urlparse

# 添加项目路径到Python路径
project_path = os.path.dirname(os.path.abspath(__file__))
jmcomic_path = os.path.join(project_path, 'JMComic-Crawler-Python-master', 'src')
sys.path.insert(0, jmcomic_path)

# 确保下载目录存在
download_dir = os.path.join(project_path, 'downloads')
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

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
            
            # 异步执行下载任务
            thread = threading.Thread(target=self.start_download, args=(comic_id,))
            thread.daemon = True
            thread.start()
            
            # 立即返回响应
            self.send_response(202)  # Accepted
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "accepted",
                "message": f"开始下载漫画 {comic_id}，请稍后查看下载目录"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def start_download(self, comic_id):
        """
        在后台执行下载任务
        """
        try:
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
            
            print(f"漫画 {comic_id} 下载完成")
        except Exception as e:
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

def run_server(host='0.0.0.0', port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, JMComicHandler)
    print(f'JMComic 下载器服务器启动在 http://{host}:{port}')
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