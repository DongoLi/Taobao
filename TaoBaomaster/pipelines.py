# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from TaoBaomaster.items import TaobaoItem


class TaobaoPipeline(object):
    def connect(self):
        '''连接数据库'''
        host = "localhost"
        dbName = "taobao"
        user = "root"
        password = "root"
        db = pymysql.connect(host, user, password, dbName, charset='utf8')
        return db   # 一定要返回连接的db
        cursorDB = db.cursor()
        return cursorDB

    def process_item(self, item, spider):
        '''数据插入taobao的数据库'''
        try:
            sql = "insert into taobao(title,link,price,comment)VALUES(%s,%s,%s,%s)"
        except Exception as e:
            print(e)
        conn=self.connect()
        cur=conn.cursor()

        cur.execute(sql,(item["title"],item["link"],item["price"],item["comment"]))

        conn.commit()
        cur.close()
        return item


class ElasticSearchPipeline(object):

    def process_item(self, item, spider):
        #将数据写入到es中
        # item.save_to_es()

        try:
            item.save_to_es()

        except Exception as e:
            print(e)



        return item
