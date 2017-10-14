# -*- coding: utf-8 -*-
import scrapy, re, urllib
from scrapy.http import Request
from TaoBaomaster.items import TaobaoItem


class TaobaoSpider(scrapy.Spider):
    name = "taobao"
    # allowed_domains = ["taobao.com"]
    start_urls = ['http://taobao.com/']

    def parse(self, response):
        keyword = '零食'
        for i in range(0, 50):
            search_url = "https://s.taobao.com/search?q=" + str(keyword) + "&s=" + str(44 * i)  #构建搜索url
            global url_lists
            url_lists = search_url
            yield Request(url=search_url, callback=self.get_item_url)



    def get_item_url(self, response):
        body = response.body.decode('utf-8', 'ignore')
        # item_id正则匹配天猫nid和isTmallt,如果是nidd中的isTmallt是True说明是在天猫上的
        item_id = r'"nid":"(.*?)".*?"isTmall":(.*?),'  #采集id，和该商品是天猫上的还是淘宝上的
        # 使⽤  compile()函数将正则表达式的字符串形式编译为⼀个Pattern对象<_sre.SRE_Pattern object at 0x00000000059A78A0>
        item_id = re.compile(item_id)
        # findall ⽅法：全部匹配，返回列表(u'550443125226', u'true')
        item_ids = re.findall(item_id, body)
        #print len(item_ids)
        for id_and_location in item_ids:
            if id_and_location[1] == "false":
                item_url = "https://item.taobao.com/item.htm?id=" + str(id_and_location[0])
                yield Request(url=item_url, callback=self.get_content)
            else:
                item_url = "https://detail.tmall.com/item.htm?id=" + str(id_and_location[0])
                yield Request(url=item_url, callback=self.get_content)

    def get_content(self, response):
        item = TaobaoItem()
        # item["link"]出现天猫和淘宝的连接
        item["link"] = response.url
        print item["link"]
        '''''''''
        忽略
        patid = 'id=(\d+)'
        thisid = re.compile(patid).findall(response.url)[0]
        get_price_url=url_lists
        #print get_price_url
        get_price_url_html= urllib.urlopen(get_price_url).read().decode("utf-8", "ignore")
        #print get_price_url_html
        reg_pprice='"nid":"'+str(thisid)+'.*?view_price":"(.*?)","'
        #print reg_pprice
        item["price"]=re.compile(reg_pprice).findall(get_price_url_html)
        # print item["link"],item["price"]
        '''''''''

        # print("*"*20)
        # print item["link"]
        # print("*" * 20)
        if 'taobao.com' in item["link"]:
            ''''在淘宝平台'''
            item["title"] = response.xpath("//h3[@class='tb-main-title']/@data-title").extract()
            # print(json.dumps(item['title'], ensure_ascii=False))
            print(item["title"])
            try:
                item["price"] = response.xpath("//em[@class='tb-rmb-num']/text()").extract()
                # item['price'] = response.xpath("//em[@class='tb-rmb-num xh-highlight'] | //em[@id='J_PromoPriceNum']/text()").extract()
                print(item['price'])
            except Exception as e:
                print(e)
            #item["original_price"]=response.xpath('//*[@id="J_StrPrice"]/em[2]/text()').extract()

            # *******收藏数需要找出对应的参数才能拼接js地址********
            # *******淘宝的交易成功数需要破解********
            '''累计评论数是要抓包才能获取到'''
            patid = 'id=(.*?)$'
            #在response.url提取id为：555826128838， 553282128376
            thisid = re.compile(patid).findall(response.url)[0]

            # Request URL:https://rate.taobao.com/detailCount.do?_ksTS=1507697457849_99&callback=jsonp100&itemId=525968806799
            commenturl = "https://rate.taobao.com/detailCount.do?callback=jsonp100&itemId=" + str(thisid)
            
            
            commentdata = urllib.urlopen(commenturl).read().decode("utf-8", "ignore")
            
            #jsonp100({"count":1910})
			# jsonp100({"count":3})
			# jsonp100({"count":0})
            reg = '"count":(.*?)}'
            item["comment"] = re.compile(reg).findall(commentdata)
            #print item["link"],item["title"][0],item["price"][0],item["comment"][0]
            yield item
        elif 'chaoshi' in item["link"]:
            '''在天猫超市平台'''
            item["title"] = response.xpath('//*[@id="J_FrmBid"]/input[@name="title"]/@value').extract()
            # *******天猫的价格隐藏起来了********
            item["price"] = 'tmallchaoshinull'

            # *******收藏数需要找出对应的参数********
            # *******淘宝的交易成功数需要破解********

            '''累计评论数是要抓包才能获取到'''
            patid = 'id=(.*?)$'
            thisid = re.compile(patid).findall(response.url)[0]
            commenturl = "https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=" + str(thisid)
            commentdata = urllib.urlopen(commenturl).read().decode("utf-8", "ignore")

            reg = '"rateTotal":(.*?),"'
            print(reg)
            item["comment"] = re.compile(reg).findall(commentdata)

        else:  # 'tmall.com' in item["link"]:
            '''在天猫平台'''
            item["title"] = response.xpath("//meta[4]/@content").extract()
            # *******天猫的价格隐藏起来了********
            item["price"] = 'tmallnull'

            #original_price='"defaultItemPrice":"(.*?)"'   #原价，可能会和现价一样
            #item["original_price"]=re.compile(original_price).findall(response.body.decode('utf-8', 'ignore'))

            # *******收藏数需要找出对应的参数********
            # *******淘宝的交易成功数需要破解********

            '''累计评论数是要抓包才能获取到'''
            patid = 'id=(.*?)$'
            thisid = re.compile(patid).findall(response.url)[0]
            commenturl = "https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=" + str(thisid)
            commentdata = urllib.urlopen(commenturl).read().decode("utf-8", "ignore")
            reg = '"rateTotal":(.*?),"'
            item["comment"] = re.compile(reg).findall(commentdata)
            yield item














            