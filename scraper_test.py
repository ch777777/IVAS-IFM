import asyncio
from douyin_tiktok_scraper.scraper import Scraper
import json

async def test_scraper():
    print("测试douyin_tiktok_scraper库...")
    
    # 创建抓取器实例
    scraper = Scraper()
    
    # 测试抖音URL
    douyin_url = "https://www.douyin.com/video/7159502929156705567"
    print(f"\n尝试解析抖音URL: {douyin_url}")
    try:
        douyin_result = await scraper.get_douyin_video_data(douyin_url)
        print(f"结果类型: {type(douyin_result)}")
        print(f"是否获取到结果: {bool(douyin_result)}")
        if douyin_result:
            # 只打印一部分重要信息
            print("部分结果:")
            print(f"  平台: {douyin_result.get('platform', '未知')}")
            print(f"  视频ID: {douyin_result.get('aweme_id', '未知')}")
            print(f"  描述: {douyin_result.get('desc', '未知')[:50]}...")
            
            # 检查是否有作者信息
            if 'author' in douyin_result:
                print(f"  作者: {douyin_result['author'].get('nickname', '未知')}")
            
            # 检查是否有视频URL
            if 'video' in douyin_result and 'play_addr' in douyin_result['video']:
                urls = douyin_result['video']['play_addr'].get('url_list', [])
                if urls:
                    print(f"  无水印视频URL: {urls[0][:50]}...")
    except Exception as e:
        print(f"解析抖音URL时出错: {str(e)}")
    
    # 测试TikTok URL
    tiktok_url = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
    print(f"\n尝试解析TikTok URL: {tiktok_url}")
    try:
        tiktok_result = await scraper.get_tiktok_video_data(tiktok_url)
        print(f"结果类型: {type(tiktok_result)}")
        print(f"是否获取到结果: {bool(tiktok_result)}")
        if tiktok_result:
            # 只打印一部分重要信息
            print("部分结果:")
            print(f"  平台: {tiktok_result.get('platform', '未知')}")
            print(f"  视频ID: {tiktok_result.get('aweme_id', '未知')}")
            print(f"  描述: {tiktok_result.get('desc', '未知')[:50]}...")
            
            # 检查是否有作者信息
            if 'author' in tiktok_result:
                print(f"  作者: {tiktok_result['author'].get('nickname', '未知')}")
            
            # 检查是否有视频URL
            if 'video' in tiktok_result and 'play_addr' in tiktok_result['video']:
                urls = tiktok_result['video']['play_addr'].get('url_list', [])
                if urls:
                    print(f"  无水印视频URL: {urls[0][:50]}...")
    except Exception as e:
        print(f"解析TikTok URL时出错: {str(e)}")
    
    # 测试混合解析
    hybrid_url = "https://www.douyin.com/video/7159502929156705567"
    print(f"\n尝试使用混合解析: {hybrid_url}")
    try:
        hybrid_result = await scraper.hybrid_parsing(hybrid_url)
        print(f"结果类型: {type(hybrid_result)}")
        print(f"是否获取到结果: {bool(hybrid_result)}")
        if hybrid_result:
            print("部分结果:")
            if 'status' in hybrid_result and hybrid_result['status'] == 'failed':
                print(f"  解析失败: {hybrid_result.get('message', '未知错误')}")
            else:
                print(f"  平台: {hybrid_result.get('platform', '未知')}")
                print(f"  视频ID: {hybrid_result.get('aweme_id', '未知')}")
    except Exception as e:
        print(f"混合解析时出错: {str(e)}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(test_scraper()) 