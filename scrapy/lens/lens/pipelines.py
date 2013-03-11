# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import MySQLdb as mdb
import demjson

class LensPipeline(object):
    def process_item(self, item, spider):
    	print "in pipeline"
    	conn = mdb.connect(host='localhost', user='root',passwd='root',db='scrapy')
        cursor   = conn.cursor()
        sql = "INSERT INTO `lens`(`name`, `image`, `url`, `info`, `append`) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql,(item['name'],item['image'],item['url'],demjson.encode(item['info']),""))
        conn.close()
        return item
