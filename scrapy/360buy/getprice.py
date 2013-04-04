#coding=utf-8
import sys 
reload(sys) 
sys.setdefaultencoding('utf-8') 

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

import MySQLdb as mdb
import demjson,os



class JingdongSpider(BaseSpider):
    name             = "jingdong_price"
    allowed_domains  = ["360buy.com","jprice.360buyimg.com"]
    start_urls       = ["http://www.360buy.com/"]

    def parse(self, response):

        con = mdb.connect(host='localhost', user='root',passwd='root',db='360buy')
        cur = con.cursor()
        sql = "select `id`,`price` from product where detail = '' order by comments desc"
        cur.execute(sql)
        results = cur.fetchall()
        for result in results:
            product_id = result[0]
            comment_level = 0
            req = Request(result[1], callback=self.parse_item)
            req.meta['product_id'] = product_id
            yield req
        con.close()


    def parse_item(self, response):
        con = mdb.connect(host='localhost', user='root',passwd='root',db='360buy')
        cur = con.cursor()
        try:
            f = open("price/%s.png"%(response.meta['product_id']),"wb")
            f.write(response.body)
            f.close()
            price = os.popen("/usr/local/bin/gocr -C '0-9.' -m 140 -i price/%s.png 2>/dev/null"%(response.meta['product_id'])).readlines()[0]
            os.remove("price/%s.png"%(response.meta['product_id']))

            p = re.compile("_")
            price = string.strip(re.sub(p,"",price))
            print response.meta['product_id'],price
            sql = "UPDATE product set detail = '%s' WHERE id=%d"%(price,response.meta['product_id'])
        except:
            sql = "UPDATE product set `detail` = 'error' WHERE id=%d" % (response.meta['product_id'])
        cur.execute(sql)
        con.close()

