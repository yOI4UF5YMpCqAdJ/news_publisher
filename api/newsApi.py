import json
import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path


class NewsApi:
    """
    news-now 项目中的API
    新闻API调用类，负责从远程API获取新闻数据
    """
    def __init__(self):
        self.base_url = "https://fork-newsnow.pages.dev/api/direct-latest"
        self.source_file = Path(__file__).parent.parent / "news-source.json"
        self.sources: List[Dict] = []
        self._load_sources()

    def _load_sources(self):
        """
        加载news-source.json文件中的新闻源配置
        """
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.sources = json.load(f)
            logging.info(f"成功加载 {len(self.sources)} 个新闻源")
        except Exception as e:
            logging.error(f"加载新闻源配置文件失败: {e}")
            self.sources = []

    def fetch_news_by_id(self, source_id: str) -> Optional[Dict]:
        """
        获取指定新闻源的最新新闻
        
        Args:
            source_id: 新闻源ID
            
        Returns:
            Dict: 新闻数据，如果发生错误返回None
            返回格式示例：
            {
                "status": "success",
                "id": "zhihu",
                "updatedTime": 1744359578095,
                "items": [
                    {
                        "id": 1893792294466990800,
                        "title": "新闻标题",
                        "url": "https://example.com",
                        "extra": {
                            "icon": "图标URL"
                        }
                    },
                    ...
                ]
            }
        """
        url = f"{self.base_url}?id={source_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data
                else:
                    logging.error(f"获取新闻源 {source_id} 失败: {data.get('message', '未知错误')}")
            else:
                logging.error(f"获取新闻源 {source_id} 失败, 状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"获取新闻源 {source_id} 时发生错误: {e}")
        return None

    def get_source_names(self) -> Dict[str, str]:
        """
        获取所有新闻源的ID和名称映射
        
        Returns:
            Dict[str, str]: 键为新闻源ID，值为新闻源名称
        """
        return {source["id"]: source["name"] for source in self.sources}

    def get_all_source_ids(self) -> List[str]:
        """
        获取所有新闻源的ID列表
        
        Returns:
            List[str]: 新闻源ID列表
        """
        return [source["id"] for source in self.sources]

# 创建实例供直接导入使用
news_api = NewsApi()

# 使用示例
if __name__ == "__main__":
    # 获取单个新闻源的数据
    zhihu_news = news_api.fetch_news_by_id("zhihu")
    if zhihu_news:
        print(f"获取到 {len(zhihu_news['items'])} 条知乎新闻")

    # 获取所有新闻源ID
    source_ids = news_api.get_all_source_ids()
    print(f"总共有 {len(source_ids)} 个新闻源")
