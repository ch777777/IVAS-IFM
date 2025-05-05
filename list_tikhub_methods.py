import tikhub_sdk_v2
import inspect

def print_api_methods(api_class, max_methods=5):
    print(f"\n=== {api_class.__name__} 可用方法 ===")
    methods = [m[0] for m in inspect.getmembers(api_class, predicate=inspect.isfunction) 
              if not m[0].startswith('__') and not m[0].endswith('with_http_info')]
    
    # 移除重复的方法名称（版本号不同的）
    unique_methods = []
    for m in methods:
        base_name = m.split('_0')[0].split('_1')[0]
        if base_name not in [um.split('_0')[0].split('_1')[0] for um in unique_methods]:
            unique_methods.append(m)
    
    # 打印方法
    for i, method in enumerate(unique_methods[:max_methods]):
        print(f"{i+1}. {method}")
    
    if len(unique_methods) > max_methods:
        print(f"... 还有 {len(unique_methods) - max_methods} 个方法未显示")

# 列出主要的API类
api_classes = [
    tikhub_sdk_v2.HybridParsingApi,
    tikhub_sdk_v2.DouyinWebAPIApi,
    tikhub_sdk_v2.TikTokWebAPIApi,
    tikhub_sdk_v2.XiaohongshuWebAPIApi
]

print("=== TikHub SDK V2 可用API ===")
for i, cls in enumerate(api_classes):
    print(f"{i+1}. {cls.__name__}")

# 为每个API类打印方法
for api_class in api_classes:
    print_api_methods(api_class) 