#coding=utf-8
import MySQLdb as mdb
import demjson
import re
from lxml import etree

import sys 
reload(sys) 
sys.setdefaultencoding('utf-8') 


def myprint(s):
	if isinstance(s, unicode): 
		print s.encode('gb2312') 
	else: 
		print s.decode('utf-8').encode('gb2312')

def main():
	con = mdb.connect(host='localhost', user='root',passwd='root',db='scrapy')
	cur = con.cursor()
	sql = "select * from lens"
	cur.execute(sql)
	results = cur.fetchall()
	# p = re.compile(r'<tr>.*?price.*?(\d+).*?Aperture')
	p1 = re.compile(r'<tr>(.*?)</tr>')
	p2 = re.compile(r'')
	items = []
	for result in results:
		item = {}
		item['name'] = result[0]
		item['image'] = result[1]
		item['url'] = result[2]
		tables = demjson.decode(result[3])
		for table in tables:
			tree = etree.HTML(table) 
			tr_nodes = tree.xpath("//tr")
			for tr_node in tr_nodes:
				kv = tr_node.xpath("./td/text()")
				if len(kv) == 2:
					item[kv[0]] = kv[1].replace(u'\xa0', u' ').encode("ascii").strip()
		print item
		sql = "INSERT INTO `lens_kv`(`name`, `kv`) VALUES(%s,%s)"
		cur.execute(sql,(result[0],demjson.encode(item)))
		
	con.close()
		
	
	
	

if __name__ == '__main__':
	main()