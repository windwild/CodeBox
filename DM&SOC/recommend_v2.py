from __future__ import division
import MySQLdb as mdb
import random
import matplotlib.pyplot as plt
import decimal
import math

# find mutual friends's mutual friends 
def recommend_friend():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()
	
	dic_weight = {}
	dic_friend = {}
	dic_isFriend = {}
	count = 0
	sql="select * from uid"
	cur.execute(sql)
	rowcount = cur.rowcount
	result1 = cur.fetchall()
	for r1 in result1:
		dic_weight[r1[0]] = 0
	sql = "select uid from uid_new order by rank desc limit 100,1000"
	cur.execute(sql)
	rowcount = cur.rowcount
	result1 = cur.fetchall()
	for r1 in result1:
		count += 1
		sql = "select fid from follow where uid = %s and weight=2"
		cur.execute(sql,r1[0])
		result2 = cur.fetchall()
		for r2 in result2:
			dic_isFriend[r2[0]] = 0
		for r2 in result2:
			if dic_weight.has_key(r2[0]):
				sql = "select fid from follow where uid = %s and weight=2"
				cur.execute(sql,r2[0])
				result3 = cur.fetchall()
				for r3 in result3:
					if r3[0] != r1[0]:
						if dic_friend.has_key(r3[0]):
							dic_friend[r3[0]] += 1
						else:
							dic_friend[r3[0]] = 1
			else:
				sql = "select fid from follow where uid = %s"
				cur.execute(sql,r2[0])
				result3 = cur.fetchall()
				for r3 in result3:
					sql = "select * from follow where uid = %s and fid=%s"
					cur.execute(sql,[r3[0],r2[0]])
					row3 = cur.rowcount
					if row3 != 0:
						sql = "update follow set weight=2 where uid=%s and fid=%s"
						cur.execute(sql,[r2[0],r3[0]])
						con.commit()
						if dic_friend.has_key(r3[0]):
							dic_friend[r3[0]] += 1
						else:
							dic_friend[r3[0]] = 1
				dic_weight[r2[0]] = 0
				sql = "select * from follow where uid = %s"
				cur.execute(sql,r2[0])
				row1 = cur.rowcount
				sql = "select * from follow where uid = %s and weight=2"
				cur.execute(sql,r2[0])
				row2 = cur.rowcount
				sql = "insert into uid values(%s,%s,%s)"
				cur.execute(sql,[r2[0],row1,row2])
				con.commit()
		for r in dic_friend:
			if dic_isFriend.has_key(r):
				sql = "insert into rem_2(uid,fid,mn,friend) values(%s,%s,%s,1)"
				cur.execute(sql,[r1[0],r,dic_friend[r]])
			else:
				sql = "insert into rem_2(uid,fid,mn) values(%s,%s,%s)"
				cur.execute(sql,[r1[0],r,dic_friend[r]])
			con.commit()		
		if count % 10 == 0:
			print count
		dic_friend.clear()
		dic_isFriend.clear()

#find common interest according to people's one-way follow
def recommend_interest():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()
	
	dic_follow={}
	dic_fn = {}
	cc = 0
	sql="select uid from uid_new order by rank desc limit 100,900"
	cur.execute(sql)
	result1 = cur.fetchall()
	for r1 in result1:
		cc += 1
		sql = "select fid from follow where uid=%s and weight=0"
		cur.execute(sql,r1[0])
		result2 = cur.fetchall()
		sum_weight = 0
		sum_count = 0
		for r2 in result2:
			sql = "select fn from user_info where id = %s"
			cur.execute(sql,r2[0])
			result3 = cur.fetchone()
			row3 = cur.rowcount
			if row3 != 0:
				weight = math.log(result3[0]-1,2)
				weight = 1 / (weight+1)
				dic_follow[r2[0]] = weight
				sum_weight += weight
				sum_count += 1
		if sum_count == 0:
			print "count is 0: ",r1[0]
			continue
		avg = sum_weight / sum_count
		s_w = sum_weight
		sum_weight = 0
		for r in dic_follow:
			sum_weight += math.pow(dic_follow[r] - avg,2)
		dev = math.pow(sum_weight/sum_count,0.5)
		if sum_weight == 0:
			print "weight is 0 :",r1[0]
			continue
		for r in dic_follow:
			if dic_follow[r] >= avg-dev:
				sql = "select uid from follow where fid = %s"
				cur.execute(sql,r)
				result4 = cur.fetchall()
				for r4 in result4:
					if dic_fn.has_key(r4[0]):
						dic_fn[r4[0]] += dic_follow[r]
					else:
						dic_fn[r4[0]] = dic_follow[r]	
		for r in dic_fn:
			dic_fn[r] = dic_fn[r] * sum_count/s_w
			sql = "select * from rem_2 where uid=%s and fid=%s"
			cur.execute(sql,[r1[0],r])
			rr = cur.rowcount
			if rr != 0:
				sql = "update rem_2 set fn=%s where uid=%s and fid=%s"
				cur.execute(sql,[dic_fn[r],r1[0],r])
				con.commit()
			else:
				sql = "insert into rem_2(uid,fid,fn) values(%s,%s,%s)"
				cur.execute(sql,[r1[0],r,dic_fn[r]])
				con.commit()
		dic_follow.clear()
		dic_fn.clear()
		if cc % 10 == 0:
			print cc

#calculate final score according to common one-way follows and common mutual friends 
def calremscore():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()

	dic = {}
	count=0
	sql = "select uid,fnum from uid_new"
	cur.execute(sql)
	rr = cur.fetchall()
	for r1 in rr:
		dic[r1[0]] = r1[1]

	sql="select uid,fnum from uid_new order by rank desc limit 0,100"
	cur.execute(sql)
	result1= cur.fetchall()
	for r1 in result1:
		count+=1
		sql = "select uid,fid,fn,mn from rem_2 where uid=%s"
		cur.execute(sql,r1[0])
		result2 = cur.fetchall()
		factor1 = 0.0586093207159
		factor2 = 21.1553713041
		f1 = factor1/(1+factor1)
		s1 = 1-f1
		f2 = factor2/(1+factor2)
		s2 = 1-f2
		for r2 in result2:
			if dic.has_key(r2[1]) == False:
				continue
			frate = r2[2]/ ((dic[r2[0]] * dic[r2[1]]) ** 0.5)
			srate = r2[3] / ((dic[r2[0]] * dic[r2[1]]) ** 0.5)
			fam = f1 * frate + s1 * srate
			sim = f2 * frate + s2 * srate
			sql = "update rem_2 set fam = %s,sim = %s where uid = %s and fid = %s"
			cur.execute(sql,[fam,sim,r2[0],r2[1]])
			con.commit()
		print count


	
def addNum():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()

	sql="select uid from uid_new"
	count=0
	cur.execute(sql)
	result1= cur.fetchall()
	for r1 in result1:
		count += 1
		sql = "select count(fid) from follow where uid=%s"
		cur.execute(sql,[r1[0]])
		result2 = cur.fetchone()
		sql = "update uid_new set fnum = %s where uid = %s"
		cur.execute(sql,[result2[0],r1[0]])
		con.commit()
		if count % 100 == 0:
			print "done",count

def addMnNum():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()

	sql="select uid from uid_new"
	count=0
	cur.execute(sql)
	result1= cur.fetchall()
	for r1 in result1:
		count += 1
		sql = "select count(fid) from follow where uid=%s and weight=2"
		cur.execute(sql,[r1[0]])
		result2 = cur.fetchone()
		sql = "update uid_new set mn = %s where uid = %s"
		cur.execute(sql,[result2[0],r1[0]])
		con.commit()
		if count % 10 == 0:
			print "done",count
	
def paintFN():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()
	
	dic = {}
	sql="select fn from user_info"
	cur.execute(sql)
	result1 = cur.fetchall()
	count = 0
	for r1 in result1:
		print r1[0]
		
		if dic.has_key(r1[0]):
			dic[r1[0]] += 1
		else :
			dic[r1[0]] = 1
	x = []*1
	y = []*1
	for i in dic :
		x.append(i)
		y.append(dic[i])
	plt.plot(x,y,'.')
	plt.show()

def paintWeight():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()
	
	dic = {}
	sql="select fid from follow where uid = 1197161814 and weight=0"
	cur.execute(sql)
	result1 = cur.fetchall()
	for r1 in result1:
		sql = "select fn from user_info where id = %s"
		cur.execute(sql,r1[0])
		r2 = cur.fetchone()
		row = cur.rowcount
		if row != 0:
			w = r2[0] -1
			weight = math.log(w,2)
			weight = 1/ (weight+1)
			if dic.has_key(weight):
				dic[weight] += 1
			else:
				dic[weight] = 1
	x = []*1
	y = []*1
	for i in dic :
		x.append(i)
		y.append(dic[i])
	plt.plot(x,y,'.')
	plt.show()		

def correctRate():
	con = mdb.connect('localhost','root','','weibo_ranker')
	cur = con.cursor()

	sql = "select uid from uid_new order by rank desc limit 0,100"
	cur.execute(sql)
	result1 = cur.fetchall()
	rowcount = cur.rowcount
	friend = 0
	allcount = 0
	notfriend = 0
	allfriend = 0
	for r1 in result1:
		count = 0
		sql = "select friend from rem_2 where uid =%s order by fam desc"
		cur.execute(sql,r1[0])
		result2 = cur.fetchall()
		allcount += 1 
		if allcount == 100:
			break
		for r2 in result2:
			if r2[0] == 1 :
				friend += 1
			else:
				notfriend += 1
			count += 1 
			if count == 50:
				break
		sql = "select count(*) from follow where uid=%s and weight=2"
		cur.execute(sql,r1[0])
		result3 = cur.fetchone()
		allfriend += result3[0]
	print "correct rate: ",friend/(50 * 100)
	print "zhaohui rate: ",friend/allfriend

if __name__ == '__main__':
	print "hello world"	
#	paintFN()
#	paintWeight()
#	recommend_friend()	
	recommend_interest()
#	addNum()
#	addMnNum()
#	calremscore()
#	correctRate()