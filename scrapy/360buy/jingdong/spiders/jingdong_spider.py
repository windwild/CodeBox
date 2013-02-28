#coding=utf-8


from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request


from jingdong.items import JingdongItem

import MySQLdb as mdb
import demjson


class JingdongSpider(BaseSpider):
    product_url = "http://www.360buy.com/products/"
    name = "jingdong"
    allowed_domains = ["360buy.com"]
    #start_urls = ["http://www.360buy.com/products/652-654-834-0-0-0-0-0-0-0-1-1-1.html"]
    start_urls = ["http://www.360buy.com/allSort.aspx"]
    urls_list = []
    # download_delay = 1

    def parse(self, response):

        hxs = HtmlXPathSelector(response)
        cats = hxs.select("//div[@class='mc']/dl/dd/em/a")
        for cat in cats:
            try:
                title = cat.select("@title").extract()[0]
                url = cat.select("@href").extract()[0]

            except:
                continue
            if(cmp(url[0:4],u"http") == 0):
                continue
            url = "http://www.360buy.com%s"%(url)
            #req = Request(url, callback=self.get_cat)
            req = Request(url, callback=self.get_item)
            req.meta['category'] = title
            req.meta['cat_key'] = ""
            req.meta['cat_value'] = ""

            yield req


    def get_cat(self, response):
        req = Request(response.url,callback=self.get_item)
        req.meta['cat_key'] = ""
        req.meta['cat_value'] = ""
        yield req

        hxs = HtmlXPathSelector(response)
        args = hxs.select("//div[@id='select']/dl")
        for arg in args:
            arg_name = arg.select("dt/text()").extract()[0]
            sub_args = arg.select("dd/div/a")
            for sub_arg in sub_args:
                sub_arg_name = sub_arg.select("text()").extract()[0]
                if(cmp(sub_arg_name,u"不限") == 0):
                    continue
                sub_arg_url = sub_arg.select("@href").extract()[0]
                sub_arg_url = "%s%s"%(self.product_url, sub_arg_url)
                req = Request(sub_arg_url, callback = self.get_item)
                req.meta['cat_key'] = arg_name
                req.meta['cat_value'] = sub_arg_name
                req.meta['category'] = response.meta['category']

                yield req


    def get_item(self, response):
        cat_key = response.meta['cat_key']
        cat_value = response.meta['cat_value']

        hxs = HtmlXPathSelector(response)
        pages = hxs.select("//div[@class='pagin fr']/a/@href").extract()
        for page in pages:
            page = "http://www.360buy.com/products/%s"%(page)
            req = Request(page,callback= self.get_item)
            req.meta['cat_key'] = cat_key
            req.meta['cat_value'] = cat_value
            req.meta['category'] = response.meta['category']
            yield req

        products = hxs.select("//ul[@class='list-h']/li")
        for product in products:
            item = JingdongItem()
            #fields = product.select("div")
            item['url'] = product.select("div[@class='p-img']/a/@href").extract()[0]
            item['pid'] = int(item['url'].split('/')[-1].split('.')[-2])
            item['name'] = product.select("div[@class='p-name']/a/text()").extract()[0]
            item['ref'] = response.url
            try:
                item['price'] = product.select("div[@class='p-price']/img/@src").extract()[0]
            except:
                item['price'] = product.select("div[@class='p-price']/strong/img/@src").extract()[0]
            try:
                item['comments'] = int(product.select("div[@class='extra']/span/a/text()").extract()[0][2:-3])
            except:
                item['comments'] = int(product.select("div[@class='extra']/a/text()").extract()[0][2:-3])
            try:
                item['rate'] = int(product.select("div[@class='extra']/span/text()").extract()[0][1:-4])
            except:
                item['rate'] = int(product.select("div[@class='extra']/span[@class='reputation']/text()").extract()[0][1:-4])

            item['cat_key'] = cat_key[0:-1]
            item['cat_value'] = cat_value
            item['category'] = response.meta['category']
            try:
                item['image'] = product.select("div[@class='p-img']/a/img/@src").extract()[0]
            except:
                item['image'] = product.select("div[@class='p-img']/a/img/@src2").extract()[0]
            
            self.save2db(item)
            yield item

    def save2db(self, item):
        conn = mdb.connect(host='localhost', user='root',passwd='root',db='360buy')
        cursor = conn.cursor()
        sql = "SELECT `args` FROM `product` WHERE `id`=%d"%(item['pid'])
        count = cursor.execute(sql)
        args_dic = {}
        if(count == 0):
            args_dic[item['cat_key']] = item['cat_value']
            item['args'] = demjson.encode(args_dic)
            # sql = "INSERT INTO `product`(`id`, `name`, `price`, `category`, `url`, `image`, `args`, `comments`, `rate`, `detail`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
            sql = "INSERT INTO `product`(`id`, `name`, `price`, `category`, `url`, `image`, `args`, `comments`, `rate`, `detail`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            # sql = "INSERT INTO `product`(`id`,`name`,`comments`,`rate`) VALUES (%s,%s,%s,%s)"
            # sql = "INSERT INTO `product`(`id`, `name`, `price`, `category`, `url`, `image`, `args`, `comments`, `rate`, `detail`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(item['pid'],item['name'],item['price'],item['category'],item['url'],item['image'],item['args'],item['comments'],item['rate'],""))
        else:
            results = cursor.fetchall()
            args_dic = demjson.decode(results[0][0])
            args_dic[item['cat_key']] = item['cat_value']
            item['args'] = demjson.encode(args_dic)
            sql = "UPDATE `product` SET `args`= '%s' WHERE `id`=%d"%(item['args'],item['pid'])
            cursor.execute(sql)



    def product_page(self, response):
        hxs = HtmlXPathSelector(response)
        hxs.select("//table[@class='Table Product_Detail']").extract()
        pass






