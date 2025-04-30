import asyncio
import logging
from main import scheduled

async def test_scheduled():
    """
    测试worker中的scheduled函数
    """
    # 配置日志输出
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 模拟Cloudflare Workers的参数
    event = {
        'time': '2025-04-14T13:23:38Z'
    }
    env = {}
    ctx = {}
    
    try:
        # 执行scheduled函数
        result = await scheduled(event, env, ctx)
        
        # 检查执行结果
        if result['status'] == 'success':
            print("测试成功！")
            print(f"返回消息: {result['message']}")
        else:
            print("测试失败！")
            print(f"错误信息: {result['message']}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    # 运行测试
    print("开始测试scheduled函数...")
    asyncio.run(test_scheduled())
