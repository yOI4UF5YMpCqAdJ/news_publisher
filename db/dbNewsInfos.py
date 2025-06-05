from datetime import datetime
import pytz
from typing import Dict, Optional, List
from .dbManager import db_manager
import logging

class dbNewsInfos:
    """
    处理news_infos表的批量写入操作
    """
    def __init__(self):
        self.db = db_manager

    def batch_insert_news(self, news_list):
        """
        批量插入新闻信息
        
        Args:
            news_list: 包含新闻信息的列表，每个元素是一个字典，包含：
                - orig_Id: 原始ID，但有问题，会有中文，很乱不统一
                - title: 新闻标题
                - url: 新闻链接
                - sourceId：原渠道
                
        Returns:
            bool: 插入是否成功
        """
        if not news_list:
            logging.warning("新闻列表为空，无需插入")
            return True

        current_time = datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
        
        # 准备批量插入的数据
        insert_data = [
            (
                news['orig_Id'],
                news['title'],
                news['url'],
                news['sourceId'],
                current_time
            )
            for news in news_list
        ]
        
        # SQL语句
        sql = """
            INSERT INTO news_infos 
            (orig_Id, title, url, sourceId,createDateTime)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            # 执行批量插入
            success = self.db.executemany(sql, insert_data)
            if success:
                self.db.commit()
                return True
            else:
                self.db.rollback()
                logging.error("批量插入新闻数据失败")
                return False
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"批量插入新闻数据时发生错误: {e}")
            return False

    def get_latest_by_sourceId(self, sourceId, limit=90):
        """
        获取指定newsId的最新记录
        
        Args:
            news_id: 新闻ID
            limit: 返回的记录数量，默认30条
            
        Returns:
            list: 返回查询结果列表，每个元素是一个元组 (id, orig_Id, title, url, createDateTime)
                  如果发生错误返回None
        """
        sql = """
            SELECT id, sourceId,orig_Id, title, url, createDateTime 
            FROM news_infos 
            WHERE sourceId = %s 
            ORDER BY createDateTime DESC 
            LIMIT %s
        """
        
        try:
            success = self.db.execute(sql, (sourceId, limit))
            if success:
                results = self.db.fetchall()
                return results
            else:
                logging.error(f"查询渠道 {sourceId} 的数据失败")
                return None
                
        except Exception as e:
            logging.error(f"查询新闻数据时发生错误: {e}")
            return None


    def insert_single_news(self, news: Dict) -> Optional[int]:
        """
        插入单条新闻信息并返回插入记录的主键ID
        
        Args:
            news: 包含新闻信息的字典，包含：
                - orig_Id: 原始ID，但有问题，会有中文，很乱不统一
                - title: 新闻标题
                - url: 新闻链接
                - sourceId：原渠道
                
        Returns:
            int: 插入记录的主键ID，如果插入失败返回None
        """
        if not self.db:
            logging.error("数据库连接不存在")
            return None
            
        current_time = datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
        sql = """
            INSERT INTO news_infos 
            (orig_Id, title, url, sourceId, createDateTime)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            success = self.db.execute(sql, (
                news['orig_Id'],
                news['title'],
                news['url'],
                news['sourceId'],
                current_time
            ))
            
            if success:
                inserted_id = self.db.get_last_insert_id()
                self.db.commit()
                return inserted_id
            else:
                logging.error("插入新闻数据失败")
                return None
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"插入新闻数据时发生错误: {e}")
            return None

    def cleanup_old_records(self, max_records: int = 5000):
        """
        清理新闻信息表中的旧记录，保留最新的指定数量记录
        
        Args:
            max_records: 最大保留记录数，默认5000条
        """
        try:
            # 首先查询总记录数
            count_query = "SELECT COUNT(*) FROM news_infos"
            cursor = self.db.connection.cursor()
            cursor.execute(count_query)
            total_count = cursor.fetchone()[0]
            
            if total_count > max_records:
                # 计算需要删除的记录数
                delete_count = total_count - max_records
                
                # 删除最旧的记录（假设有id或created_time字段用于排序）
                # 这里假设按id排序，你可能需要根据实际表结构调整
                delete_query = """
                DELETE FROM news_infos 
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT id FROM news_infos 
                        ORDER BY id DESC 
                        LIMIT %s
                    ) AS keep_records
                )
                """
                
                cursor.execute(delete_query, (max_records,))
                self.db.connection.commit()
                
                logging.info(f"成功删除 {delete_count} 条旧记录，当前保留 {max_records} 条最新记录")
                return delete_count
            else:
                logging.info(f"当前记录数 {total_count} 未超过限制 {max_records}，无需清理")
                return 0
                
        except Exception as e:
            logging.error(f"清理旧记录时发生错误: {e}")
            if self.db.connection:
                self.db.connection.rollback()
            return -1
        finally:
            if cursor:
                cursor.close()

# 创建实例供直接导入使用
db_news_infos = dbNewsInfos()
