from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys
import time

# 添加项目路径到Python路径
project_path = os.path.dirname(os.path.abspath(__file__))
jmcomic_path = os.path.join(project_path, 'JMComic-Crawler-Python-master', 'src')
sys.path.insert(0, jmcomic_path)

class JMComicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_file('index.html', 'text/html')
        elif self.path == '/style.css':
            self.serve_file('style.css', 'text/css')
        elif self.path == '/script.js':
            self.serve_file('script.js', 'application/javascript')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            comic_id = data.get('comic_id', [''])[0]
            
            if not comic_id:
                self.send_error(400, 'Missing comic_id')
                return
            
            # 执行下载
            try:
                # 尝试导入JMComic
                try:
                    import jmcomic
                    jmcomic_available = True
                except ImportError:
                    jmcomic_available = False
                
                if jmcomic_available:
                    # 使用真实的JMComic库下载
                    result = self.download_with_jmcomic(comic_id)
                else:
                    # 模拟下载
                    result = self.simulate_download(comic_id)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                error_response = {
                    'status': 'error',
                    'message': str(e)
                }
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)

    def download_with_jmcomic(self, comic_id):
        """
        使用真实的JMComic库下载
        """
        try:
            import jmcomic
            
            # 创建默认配置
            option = jmcomic.JmOption.default()
            
            # 设置下载目录
            download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
            option.download_dir = download_dir
            
            # 设置客户端配置以提高稳定性
            # 增加重试次数
            option.retry_times = 3
            # 设置超时时间
            option.timeout = 10
            
            # 实际下载漫画
            album = jmcomic.download_album(comic_id, option)
            
            return {
                "status": "success",
                "message": f"漫画 {comic_id} 下载完成",
                "path": os.path.join(download_dir, str(comic_id))
            }
        except Exception as e:
            # 提供更详细的错误信息
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "connect" in error_msg.lower():
                error_msg += "。请检查网络连接或尝试使用代理。"
            elif "404" in error_msg:
                error_msg += "。请检查漫画ID是否正确。"
            else:
                error_msg += "。这可能是由于网络问题或网站反爬机制导致的。"
            
            return {
                "status": "error",
                "message": f"下载失败: {error_msg}"
            }

    def simulate_download(self, comic_id):
        """
        模拟下载过程
        """
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
        
        return {
            "status": "success",
            "message": f"漫画 {comic_id} 下载完成（模拟）",
            "path": comic_dir
        }

    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, JMComicHandler)
    print('JMComic 下载器服务器启动在 http://localhost:8000')
    print('如果遇到网络问题，请查看 README.md 中的网络问题解决方案部分')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()