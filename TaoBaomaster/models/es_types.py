#coding= utf-8

from datetime import datetime
from elasticsearch_dsl import DocType,Date,Integer,Keyword,Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

"""
    http://localhost:9100/删掉索引article后，要重新运行es_types.py这个models,重新新建索引
    才能存入数据
"""

#链接服务器
connections.create_connection(hosts=['localhost'])


class CustomAnalyzer(_CustomAnalyzer):
    #避免ArticleType中的suggest报错
    def get_analysis_definition(self):
        return {}

# ik_analyzer对象，把analyzer=ik_analyzer（赋值）
ik_analyzer = CustomAnalyzer('ik_max_word',filter=['lowercase'])   #lowercase大小写转化


class TaoType(DocType):
    suggest = Completion(analyzer=ik_analyzer, search_analyzer=ik_analyzer)
    # title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title = Text(analyzer='ik_max_word', search_analyzer="ik_max_word", fields={'title': Keyword()})
    price = Keyword()
    link = Keyword()
    # tags = Text(analyzer='ik_max_word', fields={'tags': Keyword()})
    comment = Text(analyzer='ik_max_word')

    class Meta:
        index = 'taobao'
        doc_type = 'taobao'


    # def is_published(self):
    #     return datetime.now() >= self.published_from

if __name__ == "__main__":
    #init()根据这个类TaoType直接生成mappings
    TaoType.init()
