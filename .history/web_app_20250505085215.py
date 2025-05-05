import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
import asyncio
import shortuuid
from tikhub_interface import TikHubInterface

# 创建应用目录
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# 确保目录存在
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)

# API密钥
API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

# 创建FastAPI应用
app = FastAPI(title="TikHub Web应用")

# 设置模板和静态文件
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")

# 初始化TikHub接口
tikhub = TikHubInterface(api_key=API_KEY)

# 创建主页模板
@app.on_event("startup")
async def create_templates():
    # 创建主页模板
    index_html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikHub Web应用</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding-top: 20px; }
            .video-card { margin-bottom: 20px; }
            .video-thumbnail { width: 100%; height: auto; }
            pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto; }
            .result-container { margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">TikHub Web应用</h1>
            
            <ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="parse-tab" data-bs-toggle="tab" data-bs-target="#parse" type="button" role="tab">视频解析</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="search-tab" data-bs-toggle="tab" data-bs-target="#search" type="button" role="tab">视频搜索</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="download-tab" data-bs-toggle="tab" data-bs-target="#download" type="button" role="tab">视频下载</button>
                </li>
            </ul>
            
            <div class="tab-content" id="myTabContent">
                <!-- 视频解析 -->
                <div class="tab-pane fade show active" id="parse" role="tabpanel">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">视频解析</h5>
                            <form action="/parse" method="post">
                                <div class="mb-3">
                                    <label for="url" class="form-label">视频链接</label>
                                    <input type="text" class="form-control" id="url" name="url" placeholder="输入TikTok、抖音或小红书视频链接" required>
                                </div>
                                <button type="submit" class="btn btn-primary">解析</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <!-- 视频搜索 -->
                <div class="tab-pane fade" id="search" role="tabpanel">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">视频搜索</h5>
                            <form action="/search" method="post">
                                <div class="mb-3">
                                    <label for="platform" class="form-label">平台</label>
                                    <select class="form-select" id="platform" name="platform" required>
                                        <option value="tiktok">TikTok</option>
                                        <option value="douyin">抖音</option>
                                        <option value="xiaohongshu">小红书</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="keyword" class="form-label">关键词</label>
                                    <input type="text" class="form-control" id="keyword" name="keyword" placeholder="输入搜索关键词" required>
                                </div>
                                <div class="mb-3">
                                    <label for="count" class="form-label">结果数量</label>
                                    <input type="number" class="form-control" id="count" name="count" value="10" min="1" max="50">
                                </div>
                                <button type="submit" class="btn btn-primary">搜索</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <!-- 视频下载 -->
                <div class="tab-pane fade" id="download" role="tabpanel">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">视频下载</h5>
                            <form action="/download" method="post">
                                <div class="mb-3">
                                    <label for="download_url" class="form-label">视频链接</label>
                                    <input type="text" class="form-control" id="download_url" name="url" placeholder="输入TikTok、抖音或小红书视频链接" required>
                                </div>
                                <button type="submit" class="btn btn-primary">下载</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 结果展示 -->
            {% if result %}
            <div class="result-container">
                <h3>结果</h3>
                {% if video %}
                <div class="row">
                    <div class="col-md-6">
                        {% if video.cover_url %}
                        <img src="{{ video.cover_url }}" class="img-fluid mb-3" alt="视频封面">
                        {% endif %}
                        
                        <h4>{{ video.title or "无标题" }}</h4>
                        <p>{{ video.description or "" }}</p>
                        
                        {% if video.author %}
                        <p><strong>作者:</strong> {{ video.author.nickname or video.author }}</p>
                        {% endif %}
                        
                        <div class="d-flex gap-3 mb-3">
                            {% if video.download_url %}
                            <a href="/download-direct?url={{ video.download_url | urlencode }}" class="btn btn-success">下载视频</a>
                            {% endif %}
                            
                            {% if video.play_url %}
                            <a href="{{ video.play_url }}" class="btn btn-primary" target="_blank">播放视频</a>
                            {% endif %}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <pre>{{ result_json }}</pre>
                    </div>
                </div>
                {% elif videos %}
                <div class="row">
                    {% for video in videos %}
                    <div class="col-md-4">
                        <div class="card video-card">
                            {% if video.cover_url %}
                            <img src="{{ video.cover_url }}" class="card-img-top video-thumbnail" alt="视频封面">
                            {% endif %}
                            <div class="card-body">
                                <h5 class="card-title">{{ video.title or "无标题" }}</h5>
                                <p class="card-text">{{ (video.description or "")[:100] }}{% if video.description and video.description|length > 100 %}...{% endif %}</p>
                                {% if video.author %}
                                <p><small>作者: {{ video.author.nickname or video.author }}</small></p>
                                {% endif %}
                                <div class="d-flex gap-2">
                                    <form action="/parse" method="post">
                                        <input type="hidden" name="url" value="{{ video.share_url or '' }}">
                                        <button type="submit" class="btn btn-sm btn-primary">查看详情</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <pre>{{ result_json }}</pre>
                {% endif %}
                
                {% if download_path %}
                <div class="alert alert-success">
                    <h4>下载成功!</h4>
                    <p>文件路径: {{ download_path }}</p>
                    <a href="{{ download_url }}" class="btn btn-primary" download>下载文件</a>
                </div>
                {% endif %}
            </div>
            {% endif %}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    with open(TEMPLATES_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

# 路由
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/parse")
async def parse_video(request: Request, url: str = Form(...)):
    try:
        result = tikhub.parse_url(url)
        
        # 提取视频信息
        video = None
        if isinstance(result, dict) and "video" in result:
            video = result["video"]
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": result,
                "result_json": str(result),
                "video": video
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": {"error": str(e)},
                "result_json": str({"error": str(e)})
            }
        )

@app.post("/search")
async def search_videos(request: Request, platform: str = Form(...), keyword: str = Form(...), count: int = Form(10)):
    try:
        videos = tikhub.search_videos(platform, keyword, count=count)
        result = {"videos": videos}
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": result,
                "result_json": str(result),
                "videos": videos
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": {"error": str(e)},
                "result_json": str({"error": str(e)})
            }
        )

@app.post("/download")
async def download_video(request: Request, url: str = Form(...)):
    try:
        # 创建唯一文件名
        filename = f"{shortuuid.uuid()}.mp4"
        save_path = DOWNLOADS_DIR / filename
        
        # 下载视频
        file_path = await tikhub.download_video(url, save_path)
        if not file_path:
            raise HTTPException(status_code=500, detail="下载失败")
        
        # 创建下载URL
        download_url = f"/downloads/{filename}"
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": {"message": "下载成功"},
                "result_json": str({"message": "下载成功", "path": str(file_path)}),
                "download_path": str(file_path),
                "download_url": download_url
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "result": {"error": str(e)},
                "result_json": str({"error": str(e)})
            }
        )

@app.get("/download-direct")
async def download_direct(url: str):
    try:
        # 创建唯一文件名
        filename = f"{shortuuid.uuid()}.mp4"
        save_path = DOWNLOADS_DIR / filename
        
        # 下载视频
        file_path = await tikhub.download_video(url, save_path)
        if not file_path:
            raise HTTPException(status_code=500, detail="下载失败")
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="video/mp4"
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 启动应用
if __name__ == "__main__":
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True) 