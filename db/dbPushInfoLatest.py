from datetime import datetime
import pytz
from typing import List, Dict, Optional
from .dbManager import db_manager
import logging

class dbPushInfoLatest:
    """
    处理pushinfo_latest表的数据库操作
    """
    def __init__(self):
        self.db = db_manager

    def batch_insert_push_info(self, push_list: List[Dict]) -> bool:
        """
        批量插入推送信息
        
        Args:
            push_list: 包含推送信息的列表，每个元素是一个字典，包含：
              
                - sourceId: 渠道ID
                - sourceName: 渠道名称
                - newsInfoId: news_infos表的主键ID
                - newsType: 推送类型（stock/news）
                - status: 状态（可选，默认为0）
                
        Returns:
            bool: 插入是否成功
        """
        if not push_list:
            logging.warning("推送信息列表为空，无需插入")
            return True

        current_time = datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
        
        # 准备批量插入的数据
        insert_data = [
            (
                push['sourceId'],
                push['sourceName'],
                push['newsInfoId'],
                push['newsType'],
                push.get('status', 0),  # 如果未提供status，默认为0
                current_time
            )
            for push in push_list
        ]
        
        # SQL语句
        sql = """
            INSERT INTO pushinfo_latest 
            (sourceId, sourceName, newsInfoId, newsType, status, createDateTime)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            # 执行批量插入
            success = self.db.executemany(sql, insert_data)
            if success:
                self.db.commit()
                return True
            else:
                self.db.rollback()
                logging.error("批量插入推送信息失败")
                return False
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"批量插入推送信息时发生错误: {e}")
            return False

    def get_push_info_by_type(self, news_type: str = "news") -> Optional[List[tuple]]:
        """
        获取指定类型的所有推送信息
        
        Args:
            news_type: 推送类型（stock/news）
            
        Returns:
            List[tuple]: 返回查询结果列表，每个元素是一个元组
                        包含 (id, sourceId, sourceName, newsInfoId, newsType, status, createDateTime)
                        如果发生错误返回None
        """
        sql = """
            SELECT id, sourceId, sourceName, newsInfoId, newsType, status, createDateTime 
            FROM pushinfo_latest 
            WHERE newsType = %s
        """
        
        try:
            success = self.db.execute(sql, (news_type,))
            if success:
                results = self.db.fetchall()
                return results
            else:
                logging.error(f"查询推送类型 {news_type} 的数据失败")
                return None
                
        except Exception as e:
            logging.error(f"查询推送信息时发生错误: {e}")
            return None

    def delete_by_type_and_source(self, source_id: str, news_type: str = "news") -> bool:
        """
        删除指定新闻类型和来源的所有记录

        Args:
            source_id: 渠道ID
            news_type: 推送类型（stock/news），默认为"news"

        Returns:
            bool: 删除是否成功
        """
        if not self.db:
            logging.error("数据库连接不存在")
            return False

        sql = """
            DELETE FROM pushinfo_latest 
            WHERE newsType = %s AND sourceId = %s
        """

        try:
            success = self.db.execute(sql, (news_type, source_id))
            if success:
                rows_affected = self.db.get_rows_affected()
                self.db.commit()
                return True
            else:
                self.db.rollback()
                logging.error(f"删除记录失败，新闻类型: {news_type}，渠道ID: {source_id}")
                return False

        except Exception as e:
            self.db.rollback()
            logging.error(f"删除记录时发生错误: {e}", exc_info=True)
            return False

    def insert_single_push_info(self, push_info: Dict) -> Optional[int]:
        """
        插入单条推送信息并返回插入记录的主键ID
        
        Args:
            push_info: 包含推送信息的字典，包含：
                - sourceId: 渠道ID
                - sourceName: 渠道名称
                - newsInfoId: news_infos表的主键ID
                - newsType: 推送类型（stock/news）
                - status: 状态（可选，默认为0）
                
        Returns:
            int: 插入记录的主键ID，如果插入失败返回None
        """
        if not self.db:
            logging.error("数据库连接不存在")
            return None
            
        current_time = datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
        sql = """
            INSERT INTO pushinfo_latest 
            (sourceId, sourceName, newsInfoId, newsType, status, createDateTime)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            # 准备插入数据
            insert_data = (
                push_info['sourceId'],
                push_info['sourceName'],
                push_info['newsInfoId'],
                push_info['newsType'],
                push_info.get('status', 0),  # 如果未提供status，默认为0
                current_time
            )
            
            success = self.db.execute(sql, insert_data)
            if success:
                inserted_id = self.db.get_last_insert_id()
                self.db.commit()
                return inserted_id
            else:
                logging.error("插入推送信息失败")
                return None
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"插入推送信息时发生错误: {e}")
            return None

# 创建实例供直接导入使用
db_push_info_latest = dbPushInfoLatest()
