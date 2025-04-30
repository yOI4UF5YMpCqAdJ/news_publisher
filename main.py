import json
from pathlib import Path
import logging
from typing import List, Dict

from db.dbNewsInfos import db_news_infos
from db.dbPushInfoLatest import db_push_info_latest
from api.newsApi import news_api
from utils.logger import setup_logger

# 配置日志系统
setup_logger()

class NewsPublisher:
    """
    新闻发布管理器
    """
    def __init__(self):
        self.sources = []
        self.initialize()

    def initialize(self):
        """
        初始化函数，加载数据源配置
        """
        try:
            source_file = Path(__file__).parent / "news-source.json"
            with open(source_file, 'r', encoding='utf-8') as f:
                self.sources = json.load(f)
            logging.info(f"成功加载 {len(self.sources)} 个新闻源")
        except Exception as e:
            logging.error(f"加载新闻源配置文件失败: {e}", exc_info=True)
            self.sources = []

    def push_news(self):
        """
        推送新闻业务逻辑
        1. 遍历数据源
        2. 对每个数据源：
           - 获取数据库中的最新记录
           - 获取API的最新数据
           - 比较并插入新数据
           - 创建推送记录
        """
        logging.info("开始执行新闻推送任务...")
        for source in self.sources:
            source_id = source["id"]
            source_name = source["name"]
            logging.info(f"处理新闻源: {source_name}({source_id})")
            
            # 获取数据库中的最新记录，默认前90条
            db_records = db_news_infos.get_latest_by_sourceId(source_id)
            db_orig_ids = set()
            if db_records:
                db_orig_ids = {record[2] for record in db_records if record is not None and len(record) > 2 and record[2] is not None}
                # db_orig_ids = {record[2] for record in db_records}  # orig_Id在结果的第3个位置
            
            # 获取API的最新数据
            api_data = news_api.fetch_news_by_id(source_id)
            if not api_data or api_data.get("status") != "success":
                logging.error(f"获取新闻源 {source_id} 的API数据失败")
                continue
            
            # 处理新数据
            try:
                new_items = [item for item in api_data["items"] if "id" in item and str(item["id"]) not in db_orig_ids]
                # new_items = [item for item in api_data["items"] if str(item["id"]) not in db_orig_ids]
            except Exception as e:
                logging.error(f"发现新闻时出错:{e}")
                continue
            
            # if new_items:
            #     # 删除已发布的信息
            #     db_push_info_latest.delete_by_type_and_source(source_id)

            # 统计成功插入的数量
            success_count = 0
            for item in new_items:
                orig_id = str(item["id"])
                # 插入新的新闻记录
                news_data = {
                    "orig_Id": orig_id,
                    "title": item["title"],
                    "url": item["url"],
                    "sourceId": source_id
                }
                
                inserted_id = db_news_infos.insert_single_news(news_data)
                if inserted_id:
                    # 创建推送记录
                    push_data = {
                        "sourceId": source_id,
                        "sourceName": source_name,
                        "newsInfoId": str(inserted_id),
                        "newsType": "news",
                        "status": 0
                    }
                    push_result = db_push_info_latest.insert_single_push_info(push_data)
                    if push_result:
                        success_count += 1
            
             # 新数据处理完成后，保留最新的30条记录，删除多余的旧记录
          
            if new_items and success_count > 0:
                db_push_info_latest.delete_excess_by_source_id(source_id, keep_count=30)
                logging.info(f"source_id: {source_id}, 来源: {source_name} - 成功处理 {success_count} 条新闻")
            
        logging.info("完成新闻推送处理")

# 创建发布器实例
news_publisher = NewsPublisher()

if __name__ == "__main__":
    try:
        logging.info(f"务执开始执行")
        news_publisher.push_news()
        logging.info("任务执行完成")


    except Exception as e:
        logging.error("任务执行失败", exc_info=True)
