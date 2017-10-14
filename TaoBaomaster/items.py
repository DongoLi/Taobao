# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import redis
import scrapy
from TaoBaomaster.models.es_types import TaoType
from elasticsearch_dsl.connections import connections

# es = connections.create_connection(TaoType._doc_type.using)  # _doc_type.using链接es的一种用法
es = connections.create_connection(TaoType._doc_type.using)
redis_cli = redis.StrictRedis()  # 链接redis



def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    # global used_words
    used_words = set()  # 去重
    suggests = []

    for text, weight in info_tuple:
        if text:  # 如果传入是空字符串，就不处理
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            anylyzed_word = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_word - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class TaobaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    comment = scrapy.Field()
    original_price = scrapy.Field()


    def save_to_es(self):
        article = TaoType()
        # article.title = self["title"]
        article.title = self["title"]
        article.comment = self["comment"]
        article.link = self["link"]
        article.price = self["price"]
        article.suggest = [{"input": [], "weight": 2}]
        # article.save()
        article.save()

        # redis_cli.incr("Taobo_count")  # 将变量保存进来

        redis_cli.incr("Taobao_count")

        return
