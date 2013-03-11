#coding=utf-8


from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request


from lens.items import LensItem

import MySQLdb as mdb
import demjson


class JingdongSpider(BaseSpider):
    name             = "lens"
    allowed_domains  = ["dxomark.com"]
    start_urls       = ["http://www.dxomark.com/dakoptics/listmark.php?page=1&lensprice[]=0&lensprice[]=100000&lensrange[]=1&lensrange[]=1500&lensaperture[]=0&lensaperture[]=16&sortname=lens_date&sortorder=desc&rp=28&ranktype=usecase_portrait&viewtype=browse&urlez=http://www.dxomark.com/index.php/Lenses/Camera-Lens-Database"]
    # download_delay = 1

    def parse(self, response):
        # hxs = HtmlXPathSelector(response)
        for i in range(24):
            url = "http://www.dxomark.com/dakoptics/listmark.php?page=%d&lensprice[]=0&lensprice[]=100000&lensrange[]=1&lensrange[]=1500&lensaperture[]=0&lensaperture[]=16&sortname=lens_date&sortorder=desc&rp=28&ranktype=usecase_portrait&viewtype=browse&urlez=http://www.dxomark.com/index.php/Lenses/Camera-Lens-Database"%(i)
            req = Request(url,callback=self.get_items)
            yield req
        # cats = hxs.select("//div[@class='mc']/dl/dd/em/a")
        # for cat in cats:
        #     try:
        #         title = cat.select("@title").extract()[0]
        #         url = cat.select("@href").extract()[0]

        #     except:
        #         continue
        #     if(cmp(url[0:4],u"http") == 0):
        #         continue
        #     url = "http://www.360buy.com%s"%(url)
        #     #req = Request(url, callback=self.get_cat)
        #     req = Request(url, callback=self.get_item)
        #     req.meta['category'] = title
        #     req.meta['cat_key'] = ""
        #     req.meta['cat_value'] = ""

        #     yield req

    def get_items(self, response):
        hxs = HtmlXPathSelector(response)
        pages = hxs.select("//div[@class='block_descriptifmini']")
        for page in pages:
            url = page.select("div[@class='titre_descriptif']/a/@href").extract()[0]
            req = Request(url ,callback = self.get_detail)
            req.meta['name'] = page.select("div[@class='titre_descriptif']/a/text()").extract()[0]
            req.meta['url'] = url
            req.meta['image'] = page.select("div[@class='image_descriptiflens']/center/a/img/@src").extract()[0]
            yield req

    def get_detail(self,response):
        hxs = HtmlXPathSelector(response)
        item = LensItem()
        try:
            item['info'] = hxs.select("//div[@class='liste_descriptif']/table[@class='descriptiftab']").extract()
            print "info items:",len(item['info'])
        except:
            print "error page:",response.meta['url']
        item['name'] = response.meta['name']
        item['url'] = response.meta['url']
        item['image'] = response.meta['image']
        yield item

