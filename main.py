import sys
from pathlib import Path
import mimetypes
import threading
from wsgiref.simple_server import make_server
from urllib.parse import unquote

from loguru import logger as log
import webview
from log import log_init

log_init()

import config
from api import API

# 确保正确的 MIME 类型映射
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")

# 获取应用程序的基础路径
config.self_dir = Path(sys.argv[0]).resolve().parent

# 构建好的前端文件路径
resource_dir = Path.joinpath(config.self_dir, "resource")
if not resource_dir.exists():
    log.error(
        f"Resource directory {resource_dir} does not exist. Please build the project first."
    )
    sys.exit(1)

log.info(f"Using resource directory: {resource_dir}")


def static_file_app(environ, start_response):
    """WSGI 应用程序，用于提供静态文件服务"""
    path = environ["PATH_INFO"]

    # 移除前导斜杠
    if path.startswith("/"):
        path = path[1:]

    # 如果路径为空，默认返回 index.html
    if not path:
        path = "index.html"

    # URL 解码
    path = unquote(path)

    # 构建完整的文件路径
    file_path = resource_dir / path

    try:
        # 确保文件在资源目录内（安全检查）
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(resource_dir.resolve())):
            start_response("403 Forbidden", [])
            return [b"403 Forbidden"]

        if file_path.exists() and file_path.is_file():
            # 获取文件的 MIME 类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type is None:
                mime_type = "application/octet-stream"

            # 读取文件内容
            with open(file_path, "rb") as f:
                content = f.read()

            headers = [
                ("Content-Type", mime_type),
                ("Content-Length", str(len(content))),
            ]
            start_response("200 OK", headers)
            return [content]
        else:
            start_response("404 Not Found", [])
            return [b"404 Not Found"]

    except OSError as e:
        log.error(f"Error serving file {path}: {e}")
        start_response("500 Internal Server Error", [])
        return [b"500 Internal Server Error"]


def find_free_port(start_port=8000, max_attempts=10):
    """查找可用的端口"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise OSError(
        f"No free port found in range {start_port}-{start_port + max_attempts}"
    )


def start_static_server(port=8000):
    """启动静态文件服务器"""
    try:
        httpd = make_server("127.0.0.1", port, static_file_app)
        log.info(f"Static file server started on http://127.0.0.1:{port}")
        httpd.serve_forever()
    except OSError as e:
        log.error(f"Failed to start static server: {e}")
        raise


if __name__ == "__main__":
    # 查找可用端口并启动静态文件服务器
    try:
        server_port = find_free_port()
    except OSError as e:
        log.error(f"Failed to find free port: {e}")
        sys.exit(1)

    server_thread = threading.Thread(
        target=start_static_server, args=(server_port,), daemon=True
    )
    server_thread.start()

    api = API()

    # 创建窗口并加载前端文件
    window = webview.create_window(
        title="BxOCR - 基于PaddleOCR的票据识别工具",
        url=f"http://127.0.0.1:{server_port}",  # 使用HTTP服务器URL
        js_api=api,  # 注册API实例，使前端能够调用后端函数
        width=1000,
        height=800,
        min_size=(925, 760),
        resizable=True,
        confirm_close=not config.is_debug(),
    )

    api.set_window(window)

    # 启动应用并启用跨域支持
    webview.start(debug=config.is_debug())
