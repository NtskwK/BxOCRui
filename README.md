# BaoxiaoOCR

一款用于提取发票内容的小工具

本项目使用 PaddlePaddleOCR 以及 LLM 对发票图片的内容进行识别并提取出关键信息。

本项目基于 pywebview 构建。前端使用`React19` + `vite`构建页面，并通过 WSGI 进行访问。后端使用 [Javascript–Python bridge](https://pywebview.flowrl.com/guide/usage.html#communication-between-javascript-and-python) 进行通信(这相当于直接用 JS/TS 调用 python 函数，而不是通过http协议访问后端 api server)。详细的实现方法请见源码。

## 开发

### webview

由于 pywebview 默认使用`edgechromium`作为[引擎](https://pywebview.flowrl.com/guide/web_engine.html)，在 windows 平台你可能需要安装[Microsoft Edge WebView2](https://developer.microsoft.com/zh-cn/microsoft-edge/webview2#download)作为其依赖。

### 构建

本项目使用[`uv`](https://docs.astral.sh/uv/)作为Python的包管理器，你可以使用如下命令快速配置Python依赖。

```bash
# 如果你还没有uv，可以通过pip安装他
pip install uv

# 创建虚拟环境并安装依赖
uv sync

# 开始运行
uv run python main.py
```

#### 编译前端

```bash
cd front-end
pnpm install && pnpm build
```

#### 编译后端

```
pip install uv
uv sync
uv run pyinstall main.spec
cp -r front-end/* dist/main/front-end
```

或者你也可以参考附带的`build.bat`脚本。
