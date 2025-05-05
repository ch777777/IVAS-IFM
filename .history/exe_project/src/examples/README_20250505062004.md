# 多平台视频爬虫测试工具

本目录包含用于测试IFMCM视频爬取模块的各种脚本，支持测试不同平台的视频搜索、信息获取和下载功能。

## 支持的平台

- YouTube
- TikTok
- Bilibili
- 微博
- Facebook

## 可用的测试脚本

### 1. 单平台测试 (`multi_platform_test.py`)

用于测试单个平台的各种功能。

#### 基本用法:

```bash
# 测试YouTube搜索功能
python src/examples/multi_platform_test.py --platform youtube --query "Python tutorial" --limit 5

# 测试TikTok视频信息获取和下载
python src/examples/multi_platform_test.py --platform tiktok --url "https://www.tiktok.com/@user/video/123456789" --download

# 测试Bilibili搜索和下载
python src/examples/multi_platform_test.py --platform bilibili --query "编程教程" --limit 3 --download

# 测试Facebook带Selenium支持
python src/examples/multi_platform_test.py --platform facebook --query "programming" --selenium
```

#### 参数说明:

- `--platform, -p`: 要测试的平台
- `--query, -q`: 搜索关键词
- `--url, -u`: 视频URL，用于测试获取视频信息和下载
- `--limit, -l`: 搜索结果数量限制
- `--download, -d`: 是否测试下载功能
- `--output-dir, -o`: 视频下载目录
- `--filename, -f`: 下载的文件名（不含扩展名）
- `--cookie, -c`: Cookie字符串，用于某些平台的认证
- `--proxy`: 代理服务器地址
- `--selenium, -s`: 使用Selenium进行爬取
- `--verbose, -v`: 显示详细日志
- `--output-json`: 将测试结果保存为JSON文件

### 2. 多平台批量测试 (`test_all_platforms.py`)

一次性测试多个平台的功能。

#### 基本用法:

```bash
# 测试所有平台
python src/examples/test_all_platforms.py --query "Python tutorial"

# 测试指定平台
python src/examples/test_all_platforms.py --platforms youtube bilibili tiktok --query "Python教程"

# 测试并下载视频
python src/examples/test_all_platforms.py --platforms youtube --download

# 使用代理和Selenium
python src/examples/test_all_platforms.py --platforms facebook --proxy "http://127.0.0.1:7890" --selenium
```

#### 参数说明:

- `--query, -q`: 搜索关键词，默认为"Python tutorial"
- `--limit, -l`: 每个平台搜索结果数量限制，默认为3
- `--platforms, -p`: 要测试的平台，默认为所有支持的平台
- `--download, -d`: 是否测试下载功能
- `--output-dir, -o`: 视频下载目录，默认为"./downloads"
- `--cookie, -c`: Cookie字符串，用于某些平台的认证
- `--proxy`: 代理服务器地址
- `--selenium, -s`: 使用Selenium进行爬取
- `--verbose, -v`: 显示详细日志
- `--output-json`: 测试结果输出的JSON文件，默认为"test_results.json"

## 3. Facebook专用测试 (`facebook_api_test.py`)

专门用于测试Facebook平台的爬取功能。

#### 基本用法:

```bash
# 搜索Facebook视频
python src/examples/facebook_api_test.py search --query "Python tutorial" --limit 5

# 获取视频信息
python src/examples/facebook_api_test.py info --url "https://www.facebook.com/watch?v=123456789"

# 下载视频
python src/examples/facebook_api_test.py download --url "https://www.facebook.com/watch?v=123456789"

# 测试集成API
python src/examples/facebook_api_test.py api --url "https://www.facebook.com/watch?v=123456789" --download
```

## 注意事项

1. **网络环境**: 某些平台在特定地区可能无法直接访问，请考虑使用代理
2. **反爬虫机制**: 视频平台经常更新反爬虫机制，测试可能不稳定
3. **认证需求**: 微博和B站等平台需要认证才能获取完整数据，请提供有效的Cookie
4. **API限制**: YouTube等平台有API调用频率限制，过于频繁的测试可能导致暂时封禁
5. **Selenium需求**: Facebook等平台推荐使用Selenium进行测试，确保已安装Chrome和ChromeDriver

## 依赖项

确保已安装以下依赖:

```bash
pip install requests beautifulsoup4 selenium webdriver-manager pytube
```

对于集成API功能，安装:

```bash
pip install facebook-downloader
pip install git+https://github.com/Evil0ctal/Douyin_TikTok_Download_API.git
```

## 问题排查

- 如遇网络问题，尝试使用`--proxy`参数和代理服务
- 对于需要登录的平台，使用`--cookie`提供有效的认证信息
- YouTube搜索问题，可能与pytube库版本有关，尝试更新到最新版本
- Facebook爬取失败，尝试添加`--selenium`参数使用浏览器模拟 