#coding=utf-8
import demjson
import string
import networkx as nx
import matplotlib.pyplot as plt
import pickle as pkl
from operator import itemgetter
import numpy as np
import MySQLdb as mdb
import json
import codecs
import math
import time
import random

def isset(dic,item):
    try:
        temp = dic[item]
        return True
    except:
        return False
    
def preProcess():
    filepath1 = "/Users/windwild/sina_data/sinavip.txt"
    filepath2 = "/Users/windwild/sina_data/user_rel.csv"
    filepath3 = "/Users/windwild/Google Drive/CUHK/sina_data/json_text"
    filepath4 = "/Users/windwild/sina_data/done.txt"
    
    
    
    fp = open(filepath2,"r")
    fp2 = open(filepath4,"w")
    fp2.write('')
    fp2.close()
    fp2 = open(filepath4,"w+")
    line = fp.readline()
    array_list = {}
    for i in range(0,3000000):
        array_list['fui'] = []
        try:
            line = fp.readline()
        except:
            break
        line_arr = line.split('"')
        uid = line_arr[0][:-1]
        line = line_arr[1]
        line = line.replace("u'","'")
        items = demjson.decode(line)
        for key in items:
            array_list[key] = items[key]
        json_string = demjson.encode(array_list['fui'])
        fp2.write("%s,%s\n"%(uid,json_string))
        if(i%500==0):
            print i
        
    fp.close()
    fp2.close()
    
def calc():
    filepath = "/Users/windwild/Google Drive/CUHK/sina_data/user_rel.csv"
    G = nx.DiGraph()
    fp = open(filepath,"r") 
    fp.readline()
    array_list = {}
    for i in range(0,10):
        array_list['fui'] = {}
        line = fp.readline()
        line_arr = line.split('"')
        uid = line_arr[0][:-1]
        
        line = line_arr[1]
        print line
        line = line.replace("u'","'")
        print line
        items = demjson.decode(line)
        for key in items:
            array_list[key] = items[key]
        #print items['fui']
        print uid,i
        
        for follow in array_list['fui']:
            
            G.add_edge(uid,follow)
        
    fp.close()

    print nx.pagerank(G)
    
def preProcess2():
    filepath = "/Users/windwild/Google Drive/CUHK/sina_data/done.txt"
    filepath2 = "/Users/windwild/Google Drive/CUHK/sina_data/done2.txt"
    fp = open(filepath,'r')
    fp2 = open(filepath2,'w')
    fp2.write('')
    fp2.close()
    fp2 = open(filepath2,'w+')
    i=0
    while(1):
        i+=1
        if(i%10000 == 0):
            print i
        line = fp.readline()
        if(line == ""):
            break
        line = line.replace('"','')
        line = line.replace('[','')
        line = line.replace(']','')
        fp2.write(line)

    print "done"
    fp.close()
    fp2.close()
    
    
def get_vdic():
    print "getting V dic"
    filepath = "/Users/windwild/Google Drive/CUHK/sina_data/done2.txt"
    fp = open(filepath,'r')
    vidc={}
    for i in range(0,500000):
        if(i%10000 == 0):
            print i
        line = fp.readline()
        if(line == ''):
            break
        items = line.split(',')
        vidc[items[0]] = True
    print "done v dic"
    output = open('vdic.pkl', 'wb') 
    pkl.dump(vidc, output)
    output.close()
    return vidc
    
def load_vdic():
    print "loading vdic"
    pkl_file = open('vdic.pkl', 'rb')
    vdic = pkl.load(pkl_file)
    pkl_file.close()
    print "loaded vdic"
    return vdic
    
def init_network(vdic):
    G = nx.DiGraph()
    filepath = "/Users/windwild/Google Drive/CUHK/sina_data/done2.txt"
    fp = open(filepath,'r')
    nodes = 0
    hit = 0
    counter = {}
    counter2 = {}
    for i in range(1,1000000):
        if(i%1000 == 0):
            print i,nodes,hit,1.0*hit/nodes
            if(i%10000 == 0):
                nx.write_gml(G,"weibo_network%3d"%(i/10000))
                del G
                G = nx.DiGraph()
        
        line = fp.readline()
        if(line == ''):
            break
        items = line.split(',')
        del line
        if (items[1] == '\n'):
            G.add_node(items[0])
            continue
        uid = items[0]
        del items[0]
        nodes += len(items)
        for item in items:
            if(isset(counter,item)):
                counter[item] += 1
            else:
                counter[item] = 1
            if(isset(vdic,item)):
                temp = vdic[item]
                G.add_edge(int(uid),int(item))
                hit+=1
            else:
                if(isset(counter2,item)):
                    counter2[item] += 1
                else:
                    counter2[item] = 1
        del items
    
    fp.close()
    
    
    
    print len(counter)
    print "start sorting"
    sort_dic = dic_sort(counter)
    sort_dic2 = dic_sort(counter2)
    print "end sorting"
    
    print "start saving network"
    nx.write_gml(G,"weibo_network")
    print "end saving network"
    
    print "start saving counter"
    output = open('counter.pkl', 'wb')
    output2 = open('counter2.pkl', 'wb')
    pkl.dump(sort_dic2, output2)
    print "done sort_idic2"
    pkl.dump(sort_dic, output)
    output.close()
    output2.close()
    print "end saving counter"
    
    
    
def data2db():
    vdic = load_vdic()
    print "vdic loaded"
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    
    filepath = "/Users/windwild/sina_data/done2.txt"
    fp = open(filepath,'r')
    for i in range(1,1000000):
        if(i%100 == 0):
            print i
            con.commit()
        line = fp.readline()
        if(line == ''):
            break
        items = line.split(',')
        del line
        if (items[1] == '\n'):
            continue
        uid = items[0]
        del items[0]
        for item in items:
            if(isset(vdic,item) == False):
                sql = "INSERT INTO follow VALUES(%s,%s,1)"%(uid,item)
            else:
                sql = "INSERT INTO follow VALUES(%s,%s,0)"%(uid,item)
            cur.execute(sql)
        del items
    con.commit()
    fp.close()
    
    
def dic_sort(d,reverse=False):
    return sorted(d.iteritems(), key=itemgetter(1), reverse=True)

def load_network():
    filepath = "/Users/windwild/Google Drive/CUHK/social computing/project/weibo_network1"
    print filepath
    G = nx.read_gml(filepath)
    print "done"
    
def run_sql_insert(sql):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    rows = cur.execute(sql)
    con.commit()
    return rows
    
def new_follow2db(source, target):
    sql = "INSERT INTO follow VALUES(%s,%s)"%(source,target)
    run_sql_insert(sql)

def clean_follow_table():
    sql = "DELETE FROM follow"
    run_sql_insert(sql)
        
def counter2db():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    
    filepath = "/Users/windwild/Google Drive/CUHK/sina_data/done2.txt"
    fp = open(filepath,'r')
    nodes = 0
    hit = 0
    counter = {}
    for i in range(1,1000000):
        if(i%1000 == 0):
            print i,nodes
        
        line = fp.readline()
        if(line == ''):
            break
        items = line.split(',')
        line2 = line.split(',',1)[1]
        del line
        if (items[1] == '\n'):
            continue
        uid = items[0]
        del items[0]
        nodes += len(items)
        for item in items:
            item_int = int(item)
            if(isset(counter,item_int)):
                counter[item_int] += 1 
            else:
                counter[item_int] = 1 
        del items
    
    fp.close()
    con.close()
    
    return counter
        
def txt2db():
    clean_follow_table()
    data2db()
    
def counter2db2(counter):
    print "start counter"
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    i=0
    for key in counter:
        i += 1
        sql = "INSERT INTO counter VALUES(%d,%d)"%(key,counter[key])
        cur.execute(sql)
        if(i%50 == 0):
            con.commit()
            if(i%1000 == 0):
                print i
    con.commit()
    
    
def v_user_info2db():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    fp_e = open('error_list.txt','w+')
    error = 0
    
    arg_arr = ['_id','un','sn','sx','ad','de','iu','an','fn','mn','iv','dr','vi','wt','tg','ei','ci','bi']
    filepath = "/Users/windwild/sina_data/sinavip.txt"
    #fp = codecs.open( filepath, "r", "utf-8" )
    fp = open(filepath,'r')
    for i in range(1,1000000):
        line = fp.readline()
        line = unicode(line,'utf8')
        #print line
        if (line == ''):
            break
        arr = demjson.decode(line)
        for arg in arg_arr:
            if (isset(arr,arg)):
                if(arg in ['vi','de','tg']):
                    if(arr[arg].find('"') > -1):
                        arr[arg] = "'%s'"%(arr[arg])
                    else:
                        if(arr[arg].find("'") > -1):
                            arr[arg] = '"%s"'%(arr[arg])
                        else:
                            arr[arg] = '"%s"'%(arr[arg])
            else:
                arr[arg] = '-1'
        sql = 'INSERT INTO user_info2 VALUES (%s,"%s","%s","%s","%s",%s,"%s",%s,%s,%s,%s,%s,%s,%s,%s,"%s","%s","%s")'%(arr['_id'],arr['un'],arr['sn'],arr['sx'],arr['ad'],arr['de'],arr['iu'],arr['an'],arr['fn'],arr['mn'],arr['iv'],arr['dr'],arr['vi'],arr['wt'],arr['tg'],arr['ei'],arr['ci'],arr['bi'])
        #print sql
        try:
            cur.execute(sql)
        except:
            error += 1
            print line
            fp_e.write("%d\n"%(i))
        if(i%50==0):
            con.commit()
            if(i%1000 == 0):
                print i,error
    con.commit()
    fp.close()
    fp_e.close()
    print error
    
def user_tags():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    
    tag_arr = {}
    sql = "SELECT tg FROM user_info"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        tags = result[0].split(",")
        for tag in tags:
            if(isset(tag_arr,tag)):
                tag_arr[tag] += 1
            else:
                tag_arr[tag] = 0
    print len(tag_arr)
    i = 0
    for tag in tag_arr:
        sql = "INSERT INTO tags (`tag`,`count`)VALUES('%s',%d)"%(tag,tag_arr[tag])
        cur.execute(sql)
        i+=1
        if(i%1000 == 0 ):
            print i
    con.commit()
                
    con.close()

def vip_vip(vdic):
    i = 0
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT * FROM vip_relation limit 100000"
    cur.execute(sql)
    results = cur.fetchall()
    print "data loaded"
    for result in results:
        i+=1
        if(isset(vdic,str(result[1]))):
            sql = "INSERT INTO vip2vip VALUES(%d,%d)"%(result[0],result[1])
            cur.execute(sql)
        else:
            print "hit"
        if(i%10000==0):
            con.commit()
            print i,str(result[1])
    con.close()
            
        

def vip2vip(vdic):
    i,j,k = 0,0,0
    
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT * FROM follow"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        k += 1
        from_u = result[0]
        tos = result[1].split(',')
        for to in tos:
            j += 1
            if (isset(vdic,to)):
                sql = "INSERT INTO vip_relation VALUES(%d,%s)"%(from_u,to)
                #print sql
                cur.execute(sql)
                i += 1
                if(i%5000 == 0):
                    con.commit()
                    print k,i,j,1.0*i/j,1.0*k/320000
    con.commit()
    con.close()
    
def update_counter(vdic):
    i = 0
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT * FROM counter"
    cur.execute(sql)
    results = cur.fetchall()
    print "data fetched"
    for result in results:
        if(isset(vdic,str(result[0]))):
            sql = "INSERT INTO counter_vip VALUES(%d,%d,%d)"%(result[0],result[1],1)
        else:
            sql = "INSERT INTO counter_vip VALUES(%d,%d,%d)"%(result[0],result[1],0)
        cur.execute(sql)
        i+=1
        if(i%1000==0):
            con.commit()
            print i
    
def gen_pic():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    for i in range(20):
        lower = math.e**i
        higher = math.e**(i+1)
        sql = "SELECT count(*) FROM counter WHERE is_vip = 1 AND value >= %d AND value < %d"%(lower,higher)
        cur.execute(sql)
        results = cur.fetchall()
        for result in results:
            print i,lower,higher,result[0],math.log(result[0])
        

def get_out_count(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT count(*) FROM vip_relation WHERE `from`=%s"
    param = [uid]
    cur.execute(sql,param)
    result = cur.fetchone()
    return result[0]
    
        
def get_fans(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT `from` FROM vip_relation WHERE `to`=%s"
    param = [uid]
    cur.execute(sql,param)
    results = cur.fetchall()
    fans_string = ""
    for result in results:
        fans_string = fans_string + str(result[0]) +","
    return fans_string[:-1]
    
def get_fans_count():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT count(*) FROM vip_relation WHERE `to`=%s"
    param = [uid]
    cur.execute(sql,param)
    result = cur.fetchone()
    return result[0]
    
def update_rank_value(uid,rank_value):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "UPDATE `people_rank` SET `now` = %s WHERE `uid`=%s"
    cur.execute(sql,[rank_value,uid])
    con.commit()
    
    
def people_rank(skip=1):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    init = 0.2
    d = 0.85
    for i in range(20):
        if(i==0):
            if(skip==1):
                continue
            sql = "UPDATE `people_rank` SET `pre` = %s"
            cur.execute(sql,[init])
            con.commit()
            continue
        start_time = time.time()
        sql ="select uid from people_rank"
        cur.execute(sql)
        results = cur.fetchall()
        progress_counter=0
        for result in results:
            progress_counter+=1
            try:
                new_rank_value = 1.0-d+d*get_rank(result[0])
            except:
                #print result[0],get_rank(result[0])
                new_rank_value = 1.0-d
            update_rank_value(result[0],new_rank_value)
            if (progress_counter%100 == 0):
                percent = 1.0*progress_counter/224717
                eta_total = (time.time()-start_time)/percent
                eta = eta_total*(1.0-percent)
                eta_m = eta / 60
                eta_s = eta % 60
                print "round %d, percent:%f, eta:%d:%d"%(i,percent,eta_m,eta_s)
        sql = "UPDATE people_rank SET `pre` = `now`"
        cur.execute(sql)
        con.commit()
        print "done "+str(i)
        print time.time()-start_time
    
    
def get_rank(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    fans_string = get_fans(uid)
    sql = "SELECT SUM(`pre`/`out`) FROM `people_rank` WHERE uid in (%s)"%(fans_string)
    try:
        cur.execute(sql)
    except:
        #print uid,sql
        return 0
    rank = cur.fetchone()[0]
    return rank
    
def init_rank_out_value():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "insert into rank_value (uid,out) select uid,out from uid_out"
    cur.execute(sql)
    con.commit()
    
def get_balck_holes():
    i=0
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select id from user_info"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        i+=1
        sql = "select count(*) from uid_out where uid ="+str(result[0])
        cur.execute(sql)
        result2 = cur.fetchone()
        if(result2[0] == 0):
            sql = "insert into uid_out VALUES(%d,0,0,0)"%(result[0])
            cur.execute(sql)
        if(i%1000 == 0):
            print i
            con.commit()
    con.commit()

def people_rank_bh(backup_flag = 0, black_hole_flag = 1):
    d = 0.85
    user_dic = {}
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select uid,pr,`out`,sn from people_rank4"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        user_dic[result[0]] = [result[1],result[2],result[3],0.15]
    del results
    print "inited user dictionary!"
    
    for iter_time in range(1,100):
        print "start iteration "+str(iter_time)
        start_time = time.time()
        progress_counter=0
        for uid in user_dic:
            sql = "select `from` from vip_relation where `to` = %s"
            cur.execute(sql,[uid])
            results = cur.fetchall()
            sum = 0.0
            for result in results:
                try:
                    sum += user_dic[result[0]][0]/user_dic[result[0]][1]
                except:
                    pass
            del results
            user_dic[uid][3] = 1.0 - d + d * sum
            progress_counter+=1
            if(progress_counter%500==0):
                total_time = int(time.time()-start_time)
                percent = 1.0*progress_counter/319797
                eta_total = total_time/percent
                eta = eta_total*(1.0-percent)
                eta_m = eta / 60
                eta_s = eta % 60
                tt_m = total_time / 60
                tt_s = total_time % 60
                print "round %d, percent:%f, eta:%d:%d total_time:%d:%d"%(iter_time,percent,eta_m,eta_s,tt_m,tt_s)
        
        print "saving data to database!"
        i=0
        for uid in user_dic:
            i+=1
            sql="UPDATE people_rank4 SET `pr`=%s where `uid`=%s"
            cur.execute(sql,[user_dic[uid][3],uid])
            user_dic[uid][0] = user_dic[uid][3]
        con.commit()
        
        if(black_hole_flag == 1):
            print "solving black hole!"
            sql = "select sum(pr)/325360 from people_rank4 where `out`=0"
            cur.execute(sql)
            pr_ave = cur.fetchone()[0]
            sql = "UPDATE people_rank4 set pr = pr + %f" % (pr_ave)
            cur.execute(sql)
            con.commit()
            
        if(backup_flag == 1):
            print "backuping PR"
            sql = "insert into page_rank_log(uid,pr,sn)(SELECT uid,pr,sn FROM `people_rank3` order by pr desc)"
            cur.execute(sql)
            con.commit()
        print "clear!"
        print "total time:" + str(int((time.time()-start_time)/60))
        
def get_jumps():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    log1={}
    log2={}
    change={}
    sql = "SELECT uid,rank from people_rank_r1"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        log1[result[0]] = result[1]
    sql = "SELECT uid,rank from people_rank_r2"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        log2[result[0]] = result[1]
    for uid in log1:
        change[uid] = log2[uid]-log1[uid]
    for uid in change:
        sql="insert into change_rank VALUES(%d,%d)"%(uid,change[uid])
        cur.execute(sql)
    con.commit()
        
def vip_filter(guanzhu_string):
    vdic = load_vdic()
    vusers_dic = {}
    users_dic = {}
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    results = demjson.decode(guanzhu_string)
    vuser_string = ""
    for result in results['ids']:
        if(isset(vdic,str(result))):
            vuser_string = vuser_string + str(result) +","
    vuser_string = vuser_string[:-1]
    sql = "select uid,sn,log(log(pr)-6*log(fn)+100) as score,pr,fn from people_rank4 where uid in (%s) and log(pr)>-1 and log(fn)<12 order by score desc"%(vuser_string)
    print sql
    cur.execute(sql)
    vusers = cur.fetchall()
    for vuser in vusers:
        vusers_dic[vuser[0]] = (vuser[1],vuser[2],vuser[3],vuser[4])
    sql = "select `from`,`to` from vip2all where `from` in (%s)"%(vuser_string)
    cur.execute(sql)
    items = cur.fetchall()
    for item in items:
        if(isset(vusers_dic,item[0])):
            if(isset(users_dic,item[1])):
                users_dic[item[1]] += vusers_dic[item[0]][1]
            else:
                users_dic[item[1]] = vusers_dic[item[0]][1]
    #print users_dic
    i=0
    sql = "delete from results where type=1"
    cur.execute(sql)
    for item in sorted(users_dic.items(),key=lambda d:d[1],reverse=True):
        i+=1
        sql = "insert into results VALUES(1,'%d','%f')"%(item[0],item[1])
        cur.execute(sql)
        if(i==100):
            break

    i=0
    sql = "delete from results where type=2"
    cur.execute(sql)
    for item in sorted(vusers_dic.items(),key=lambda d:d[1][1],reverse=True):
        i+=1
        sql = "insert into results VALUES(2,'%d','%s:%f:%f:%f')"%(item[0],item[1][0],item[1][1],math.log(item[1][2]),math.log(item[1][3]))
        cur.execute(sql)
        if(i==100):
            break
    con.commit()
    con.close()
    return item
    
def fix_bh_user():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select id,sn,vi,fn from user_info"
    cur.execute(sql)
    results = cur.fetchall()
    i,hit=0,0
    for result in results:
        i+=1
        sql="select count(*) from people_rank4 where uid=%d"%(result[0])
        cur.execute(sql)
        if(cur.fetchone()[0] == 0):
            sql='insert into people_rank4 VALUES(%d,0.2,0,"%s","%s",%d,-1)'%(result[0],unicode(result[1],"utf-8"),unicode(result[2],"utf-8"),result[3])
            hit+=1
            try:
                cur.execute(sql)
            except:
                print "error:"+sql
        if(i%10000==0):
            print i,hit
    con.commit()
    
    
def update_flag2peoplerank():
    i=0
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select * from `temp`"
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        i+=1
        if(i%500==0):
            print i
        sql = "update people_rank3 set flag=%d where uid=%s"%(result[1],result[0])
        cur.execute(sql)
    con.commit()
    
def plot_pr_fn():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT log(pr),log(fn),sn FROM people_rank3 WHERE pr!=0.181388 ORDER BY rand() LIMIT 50000"
    cur.execute(sql)
    points = cur.fetchall()
    plt.figure(figsize=(32,32), dpi=80)
    i=0
    for point in points:
        i+=1
        plt.plot(point[0],point[1],'.',color='black')
        if(i%1000==0):
            print i
    x = np.arange(-2,0,1)
    y1 = [math.log(10000) for ele in x]
    y2 = [math.log(20000) for ele in x]
    y3 = [math.log(100000) for ele in x]
    plt.plot(x,y1,color='red',linewidth=5)
    plt.plot(x,y2,color='red',linewidth=5)
    plt.plot(x,y3,color='red',linewidth=5)
    plt.savefig('pr_fn.png',dpi=80)
    
def decomplex(G,uid,node_number_threshold = 100):
    if(len(G.nodes()) < node_number_threshold):
        return 
    else:
        ave_degree = 1.0*(sum(G.degree().values()))/len(G.nodes())
        for node in G.nodes():
            if(G.degree(node) < ave_degree and node != uid):
                G.remove_node(node)
        decomplex(G,uid,node_number_threshold)
    
    
def find_clique(uid,p_ave_degree=50):
    buffered = get_buffer_clique(uid)
    if(buffered != False):
        return buffered
    G = nx.DiGraph()
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select uid from (select `to` from vip_relation where `from`=%d) as vip left join people_rank4 on vip.`to`=people_rank4.uid where flag < 1"%(uid)
    
    cur.execute(sql)
    users = cur.fetchall()
    user_list = [uid]
    for user in users:
        G.add_edge(uid,user[0])
        user_list.append(user[0])
    for user in user_list:
        sql = "select uid from (select `to` from vip_relation where `from`=%d) as vip left join people_rank4 on vip.`to`=people_rank4.uid where flag < 1"%(user)
        cur.execute(sql)
        results = cur.fetchall()
        for result in results:
            if(result[0] in user_list):
                G.add_edge(user,result[0])
    if(len(G.nodes()) == 0):
        save_clique(uid,[])
        return []
    
    #decomplex by deleting nodes
    decomplex(G,uid,200)
    
    dG = G.to_undirected(True)
    sub_graph_node_list = dG.neighbors(uid)
    sub_graph_node_list.append(uid)
    dG = dG.subgraph(sub_graph_node_list)
    
    dG_node_number = len(dG.nodes())
    cliques = nx.cliques_containing_node(dG,uid)
    clique_user_dic = {}
    for clique in cliques:
        if(len(clique) > 2):
            for user in clique:
                if(user == uid ):
                    continue
                if(isset(clique_user_dic,user)):
                    clique_user_dic[user] += 1
                else:
                    clique_user_dic[user] = 1
    clique_user_arr = sorted(clique_user_dic.iteritems(), key=itemgetter(1), reverse=True)
    save_clique(uid,clique_user_arr)
    return clique_user_arr
    
def break_graph(G):
    G = G.copy()
    max_degree = sorted(nx.degree(G).values(),reverse=True)[0]
    print "max degree",max_degree
    for node in G.nodes():
        if(G.degree(node) == max_degree):
            G.remove_node(node)
            break
    components = nx.connected_component_subgraphs(G)
    print components
    
    
def print_users_info(user_list):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    for user in user_list:
        sql="select sn,vi from user_info where id=%d"%(user)
        cur.execute(sql)
        info = cur.fetchone()
        print unicode(info[0],"utf-8"),unicode(info[1],"utf-8")
    con.close()

def print_user_info_dic(user_dic):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    for user in user_dic:
        sql="select sn,vi from user_info where id=%d"%(user[0])
        cur.execute(sql)
        info = cur.fetchone()
        print unicode(info[0],"utf-8"),unicode(info[1],"utf-8")
    print ""
    con.close()

def runsql():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    #sql = 'INSERT INTO vout (SELECT `from_uid`,count(*) as `out` FROM `follow` WHERE flag=0 group by `from_uid`)'
    sql="delete from vip2all"
    #sql = 'insert into people_rank4(uid,`out`,sn,vi,fn) select uid,`out`,sn,vi,fn from vout,user_info2 where vout.uid=user_info2.id'
    cur.execute(sql)
    con.commit()
    
def draw_spring_graph(G,cliques = False):
    node_color=[float(G.degree(v)) for v in G]
    if(cliques != True):
        color = 0.0
        color_dic={node:0.0 for node in G.nodes()}
        cliques = sorted(cliques, key=len, reverse=True)
        for clique in cliques:
            color += 20
            for node in clique:
                color_dic[node] = color
        node_color = [color_dic[node] for node in color_dic]
    plt.figure(figsize=(32,32))
    pos=nx.spring_layout(G,iterations=500)
    #print node_color
    node_size_base = 50000 / len(G.nodes())
    nx.draw_networkx_nodes(G,pos,node_size=[G.degree(n) * node_size_base for n in G.nodes()],alpha=0.5,node_color=node_color)
    nx.draw_networkx_edges(G,pos,alpha=0.2)
    #nx.draw_networkx_labels(G,pos,font_size=6)
    plt.axis('off')
    #plt.show()
    plt.savefig('social_circle.png')
    
    
def get_follow_list(uid):
    follow_list = []
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select `to` from vip_relation where `from`=%d"%(uid)
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        follow_list.append(result[0])
    return follow_list
    
def gd(x,a,b):
    return 1/(math.sqrt(2*math.pi)*a)*(math.e**(-(x-b)**2/(2*a**2)))

def rec_by_clique(uid=0):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    
    vdic = load_vdic()
    if(uid != 0):
        pass
    else:
        uid=1690900610
    follow_list = get_follow_list(uid)
    vlist=[]
    for user in follow_list:
        if(isset(vdic,str(user))):
            vlist.append(user)
    user_string =""
    for user in vlist:
        user_string += str(user)+','
    user_string = user_string[:-1]
    print user_string
    sql = "select uid,pr,fn,sn,vi from people_rank4 where uid in (%s)"%(user_string)
    print sql
    cur.execute(sql)
    results = cur.fetchall()
    user_dic = {}
    for result in results:
        weight = gd(math.log(result[1]),2,2)
        user_dic[result[0]] = [weight,result]
    
    user_dic = sorted(user_dic.iteritems(),key=itemgetter(1),reverse=True)
    print type(user_dic)
    for user in user_dic:
        print user[0],user[1][0],unicode(user[1][1][4],'utf-8'),unicode(user[1][1][3],'utf-8')
        
        
def get_user_info(uid):
    user_info_dic = {}
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql="select uid,pr,`out`,sn,vi,fn,flag from people_rank4 where uid=%d"%(uid)
    cur.execute(sql)
    info = cur.fetchone()
    user_info_dic['uid'] = info[0]
    user_info_dic['pr'] = info[1]
    user_info_dic['out'] = info[2]
    user_info_dic['sn'] = unicode(info[3],'utf-8')
    user_info_dic['vi'] = unicode(info[4],'utf-8')
    user_info_dic['fn'] = info[5]
    user_info_dic['flag'] = info[6]
    con.close()
    return user_info_dic
    
def print_one_user_info(uid,args=False):
    user_info_dic = get_user_info(uid)
    print user_info_dic

def is_real_user(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select count(*) from people_rank4 where uid=%d and flag<=0"%(uid)
    cur.execute(sql)
    if(cur.fetchone()[0] == 0):
        return False
    return True
    
def save_clique(uid,user_list):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    buffer_string = demjson.encode(user_list)
    sql = "INSERT INTO buffer VALUES(%d,'%s')"%(uid,buffer_string)
    cur.execute(sql)
    con.commit()
    con.close()
    
def get_buffer_clique(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT * from buffer where uid=%d"%(uid)
    cur.execute(sql)
    result = cur.fetchone()
    con.close()
    if(result == None):
        return False
    else:
        print "hit clique uid:",uid
        return demjson.decode(result[1])
    
def rec_by_clique2(uid=0,s_percent=0.5,s_percent_ff=0.5):
    user_info_dic = get_user_info(uid)
    print user_info_dic['uid'],user_info_dic['sn'],user_info_dic['vi'],user_info_dic['pr']
    result_dic = {}
    uid_clique = find_clique(uid)
    save_clique(uid,uid_clique)
    len_clique = len(uid_clique)
    if(len_clique==0):
        return []
    
    i=0
    max_weight = math.log(uid_clique[0][1]+2)
    for user in uid_clique:
        i += 1
        if(i>len_clique*s_percent) or (i > 20):
            break
        #print_one_user_info(user[0],user[1])
        weight = math.log(user[1]+2) / max_weight
        ff_clique = find_clique(user[0])
        
        j=0
        len_ff = len(ff_clique)
        if(len_ff == 0):
            continue
        max_weight_ff = math.log(ff_clique[0][1]+2)
        for ff in ff_clique:
            j+=1
            if(j>len_ff*s_percent_ff) or (j > 20):
                break
            #print_one_user_info(ff[0],ff[1])
            if(isset(result_dic,ff)):
                result_dic[ff[0]] += weight * math.log(ff[1]+2) / max_weight_ff
            else:
                result_dic[ff[0]] = weight * math.log(ff[1]+2) / max_weight_ff
    
    result_arr = sorted(result_dic.iteritems(),key=itemgetter(1),reverse=True)
    result_arr2=[]
    for user in result_arr:
        if(is_real_user(user[0])):
            result_arr2.append(user)
    return result_arr2
    
        
def evaluate_function(uid,result_arr,use_time,node_number):
    user_dic={}
    for user in result_arr:
        user_dic[user[0]] = True
    len1=len(result_arr)
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select uid from (select `to` from vip_relation where `from`=%d) as vip left join people_rank4 on vip.`to`=people_rank4.uid where flag<2"%(uid)
    cur.execute(sql)
    results = cur.fetchall()
    len2 = len(results)
    for result in results:
        user_dic[result[0]] = True
    len3 = len(user_dic)
    user_info_dic = get_user_info(uid)    
    if(len1 == 0):
        rate = 1.0
    else:
        rate = 1.0*(len1+len2-len3)/len1
    sql = "INSERT INTO eva_result(`uid`, `rec_num`, `follow_num`, `rate`, `sn`, `vi`, `fn`, `pr`, `time`) VALUES(%d,%d,%d,%f,'%s','%s',%d,%f,%f)"%(uid,len1,len2,rate,user_info_dic['sn'],user_info_dic['vi'],user_info_dic['fn'],user_info_dic['pr'],use_time)
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()
    return [len1,len2,len3,rate]


def ramdom_select(number):
    result_list = []
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql="select uid from people_rank4 where flag<1 and pr>0.8 and pr<1.5"
    cur.execute(sql)
    uids = cur.fetchall()
    for i in range(number):
        index = random.randrange(len(uids))
        result_list.append(uids[index][0])
    con.close()
    return result_list
    
def select_peak(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    user_list=[uid]
    sql = "select uid from (select `to` from vip_relation where `from`=%d) as vip left join people_rank4 on vip.`to`=people_rank4.uid where flag < 1"%(uid)
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        user_list.append(result[0])
    con.close()
    return user_list

def save_result(uid,result_arr):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "INSERT INTO results_buffer VALUES(%d,'%s')"%(uid,demjson.encode(result_arr))
    cur.execute(sql)
    con.commit()
    con.close()
    
def get_buffered_result(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT * FROM results_buffer WHERE uid=%d"%(uid)
    cur.execute(sql)
    result = cur.fetchone()
    con.close()
    if(result == None):
        return False
    else:
        print "result hit",uid
        return demjson.decode(result[1])
        
def my_1d_function(uid):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "SELECT pr,fn FROM people_rank3 WHERE uid=%d"%(uid)
    cur.execute(sql)
    result = cur.fetchone()
    con.close()
    return math.log(result[0]) - math.log(result[1]) * 6 + 20
        
def method01():
    uid_list = select_peak(1639127253)
    for uid in uid_list:
        start_time = time.time()
        buffered_result = get_buffered_result(uid)
        if(buffered_result != False):
            result_arr = buffered_result
        else:
            result_arr = rec_by_clique2(uid)
        save_result(uid,result_arr)
        use_time = time.time() - start_time
        eva_result = evaluate_function(uid,result_arr,use_time,0)
        print eva_result[0], eva_result[1], eva_result[2], eva_result[3]
        print ""

def windwild_ana(user_string):
    vdic = load_vdic()
    vusers_dic = {}
    users_dic = {}
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    results = demjson.decode(user_string)
    vuser_string = ""
    for result in results['ids']:
        if(isset(vdic,str(result))):
            vuser_string = vuser_string + str(result) +","
    vuser_string = vuser_string[:-1]
    sql = "select uid,sn,5*log(pr)-6*log(fn) as score,pr,fn from people_rank4 where uid in (%s) order by score desc"%(vuser_string)
    print sql
    cur.execute(sql)
    vusers = cur.fetchall()
    for vuser in vusers:
        vusers_dic[vuser[0]] = (vuser[1],vuser[2],vuser[3],vuser[4])
        print unicode(vuser[1],'utf-8')
        my_input = raw_input('your opion:')
        if(my_input == "+"):
            plt.plot(math.log(vuser[3]),math.log(vuser[4]),'k+')
        else:
            plt.plot(math.log(vuser[3]),math.log(vuser[4]),'k*')
    plt.savefig('windwild_ana.png')
            
    
def method02():
    follow_string = '{"ids":[1999990425,1922304997,1761179351,2447745885,1889806537,1705093571,1915548291,1407425245,1866882821,2708425425,3143734843,1914357491,2310964602,2247657845,1646218964,1578028253,1639208147,1632066980,1761053495,1804950771,1734349735,1624087025,2855640462,1655740651,2482801795,2665909251,1949708673,1827590551,1727421522,1763133130,2069137037,1877564875,1929644930,2250770035,2399012781,1746504362,2013429572,2107383992,1650081652,1197069394,2642032423,2256269763,2180272614,1865943825,1805187123,2379852192,1265020392,1417587570,2214247937,2957438054,2072523893,1974528673,1273609757,2108165354,2794578770,2060750830,1654619934,1251517007,1582459022,2128908815,2009948983,2074377952,2852680165,2177015850,1742571124,1497035431,1951129281,1769297592,1756398905,1747389861,2392261910,1872109493,2672020931,1684953923,1194774797,2830723120,2058865994,1731453207,1684454151,1309690680,1888209427,2008545807,1831645731,1774959772,1741692611,2711736393,1946365995,2101940163,1861417295,1748128465,1790008304,1866155660,2811633743,1864177954,1815208443,2168995901,1729610834,1738657544,1651821482,1704145013,1652709933,1880424095,2162572710,1249234963,1846044211,1675681434,2122490441,1844785547,2117462225,1750070171,2273017240,1907196994,1232540057,1799705357,1663118494,2951191642,1858386852,1764105342,1912726703,1888447407,1642482194,1678129472,1784501333,2510049230,2115297880,1658230733,1400220917,1816398273,1722205111,1655601927,1919238487,1628542265,2675905163,1951028903,1658735622,1663903655,1218449722,2137526157,1814209473,1653307180,2675732961,2202058841,1768458170,1920406927,2124270327,2111114141,2572822887,2420767405,1616313084,1836955377,2764028813,1861500233,1583427910,1829612781,1929431633,1892998227,1658686183,1820229951,1235277044,1761201063,1898381543,1891605040,2294342582,1797031783,1887862373,2366458912,1642051034,1900033262,1900084192,1378010090,1265891030,1845950835,1783826025,1686920444,2443022943,1803346527,1088234725,2654573151,1731424125,1922358605,1502591714,1640328892,1292105442,1729162020,1850988623,1018605431,1963412001,1919512224,1847161173,1915954881,1833565007,1675464430,1751313480,1170999921,1130183787,1872043064,1749101153,1644635542,1739290340,1978406075,2417258505,1528440090,1512296563,1934489032,2308280784,1916762641,2613995905,1824957965,1991205442,1692238114,1865472281,1916705721,2305721603,1736032945,2156967145,1832067323,1700051610,2564830743,2273229020,2608412277,2279131215,10503,1988712133,1816361510,1994876027,1747631044,2612381691,1774173043,1691769320,2091896172,1643179744,1885656943,2648201300,1653123814,1189729754,1782403985,1461037710,1784344563,1627825392,1882854902,1738535843,1629810574,2075992307,2585782307,1839204587,1635878447,2104127127,1827120293,2128830253,1759095717,1426858784,1731027372,1262574743,1871902464,2051793483,1042154874,1825634927,1864165950,1216854383,1751453907,1752891094,2127318833,1627734210,1948466801,1279199982,1175618845,1864727447,1711605755,1261848117,1788880342,1697346010,2313658692,2521990780,1748046960,1504149544,2270441163,1772489667,2285967533,1576989581,2470296621,1963478743,1164190195,1880709794,2310686612,1806905500,1831202675,1887341152,1087814873,1655924355,2261146447,2003797663,1909836045,1787811865,1051862451,1766788303,2350420391,1689944994,1868026715,2156927867,1803130413,1720079574,1564361787,1806586033,1677640694,1923406437,2024413127,1593630341,1970583115,2102532093,2034296520,1736642743,1688161242,1659970177,1301404355,1853119303,1991029844,1750767227,1280329503,1686163673,1657810371,1630461754,1820807330,2081315145,1679087640,1766665222,2039012257,1624639823,1644059215,1892436682,1805612512,1740334623,1832841364,2313850667,2463261612,2022017755,1783203711,2402139117,2102138493,2048600345,1932735015,1919243167,1563894614,1805324217,1839159164,1922695813,1778332085,1636190514,1688541660,1300659801,2144502895,1483500601,1836570081,1144014705,1769534521,1881406207,1815507001,1724798542,1713911071,2017967077,1909422885,1684786511,1494759712,1355610915,2093492691,1658892874,1272222963,1939997053,1638882811,1771077441,1832797203,1853783333,1823503551,1919347627,1662047260,1971575311,1796099013,2120241675,1836483953,1914122963,1948165955,1866917945,1678008445,1766299691,1772689277,2110794314,1689882032,2108377052,2153807481,1873625985,1613380424,1684197391,1733998810,2137167015,1710406277,1184777244,1853896487,2101534905,1751201045,1576119025,1822554773,1789436050,1840195061,1625684190,1764074447,1678034163,1644167525,1818500633,1765267692,1614129857,1862034191,1197161814,1690900610,1718576913,1617500982,1891616631,1398667565,1764078023,1820008585,1787219177],"next_cursor":0,"previous_cursor":0,"total_number":419}'
    follow_string = '{"ids":[2725476103,1867902484,2175137232,1244944200,1800292413,1571497285,1915548291,1847982423,1735559201,1911980657,1401880315,1939498534,1701886454,1710406277,1657706754,1869059970,1142429025,1742893655,2659503961,1654619934,1960047167,1433596734,1212040547,1340529235,1658383972,1921046714,1571860783,2020301915,1217324583,1829488040,1840195061,1870164840,1905884057,1638781994,1497035431,1853795897,1872712102,1672272373,2828925207,2365769501,2145291155,2589512460,2604214117,2710838571,2235572234,1976774857,2831997532,1873408564,1627489513,2625375393,1864177954,1634798410,1748882397,1664975327,2700537742,1873012210,1560910162,1654342844,1768352230,1624458857,1846302951,2038757084,1760136201,1869937482,2497497994,1405947625,1662047260,1915300055,1761383964,2857596964,1867480032,1670518271,1641983193,1267685444,1642017291,1507274672,1883685092,2986786734,2959416774,2635504977,1746139940,1774978073,1249193625,1854283601,1618051664,1670071920,1563815015,1704116960,1255849511,1980923321,1816011541,1196235387,1644492510,1642909335,1195403385,1212812142,1821898647,1198920804,1692544657,1188552450,1649005320,1752467960,1653689003,1682352065,1730336902,1639498782,2132619841,2305670113,1711394437,2403292733,2154575087,1233536692,2216755173,1781379945,1891407500,1266321801,1872167594,1917056754,1674081142,1822549862,1873250714,1769251257,1340360661,2413576542,1760452944,1749214017,1827652007,1870336322,1628850013,1721325690,1728069367,1851503165,1705278515,2093492691,1355610915,1645171780,1630461754,1627825392,2672012734,2255725144,1675464430,1850988623,1400220917,2115297880,1784501333,2273017240,2708425425,1815208443,1092413824,1614282004,1708942053,1813080181,1857474330,1197161814,1904769205,1437229625,1687445053,1663418681,2147378853,2269176003,2345193194,1187986757,1749127163,1403866102,2076119287,1774986382,1241330914,1657681711,1558247760,1994402690,1886482057,1640663757,2375545650,1692677257,1182391231,1599464160,1750070171,1873295444,1193491727,1916113004,1236392942,1793285524,1691667670,1652566713,1642720480,1889102490,1951443111,1345566427,1953878117,1568075952,1993715557,1770764183,1832549915,1620986860,1787567623,2355225860,1195031270,1812758754,1191258123,1878986682,1878458114,1829330340,2811930010,1066917894,1243441531,1930378853,1726406904,2272336580,2452933723,2155035021,1684388950,2142166543,1182389073,2881402282,2181587415,1631731490,1577794853,1066644571,1283022704,2640779347,1878546883,1640659917,1589175662,2887339314,1642027101,2166092567,2200773043,1807123330,1603107245,1721828837,2320711045,1847285331,1220291284,2155226773,1904178193,1622004114,1794290350,2234137897,1827293387,1880130892,2255423004,2772640101,2670402163,2424876734,2196865820,1758277353,1710847085,2758197137,1893549044,1404927945,2797440223,2610501397,2086964427,1962310741,1902538057],"next_cursor":0,"previous_cursor":0,"total_number":255}'
    follow_string = '{"ids":[1692558512,1692569500,1454560380,1947837535,1663418681,1630187317,3102273263,2183421475,2529882607,1822519087,3130318443,1654974414,1400870002,2826785055,1116143582,2952668222,1748559003,1971776345,1055926482,1668218230,1657422865,1750073402,1656964711,1655689017,1988124285,2535692962,2751210255,1640050005,2135003075,1972707771,1461522430,1495197303,2210992617,1652932423,1650305231,1954493335,1040568937,1764378973,1464532414,1848720311,1828477757,2365758410,2108057087,2549689004,1894146945,2158872872,1642011032,2162752440,1683601552,1416895904,1667886882,2213609734,1942709733,1627417227,1641287674,2049553810,1658417270,2128594661,1569063525,1884473311,1688135160,1653448197,1710176135,1974808274,1237285712,1887131874,1366091891,1495041353,1960289903,1646446167,1401313454,1862029690,1693835694,1619803023,1407649650,1195403385,2887339314,1943462967,1721371132,1692722700,1244423705,1634074550,1812803511,2493289591,1895822993,1248889264,1578997200,1249935904,1251600717,2231309987,1414874625,1909540643,1865930572,2002254045,2513098153,1716908045,2378745285,1601423645,1761587972,1712189470,1826291175,1938166551,1645369650,1650692047,1714086647,1799738983,1629729431,1497035431,102942,1694592453,1400229064,2496213213,1866038992,2136664345,1820081987,1749127163,1708942053,2150311773,2282929711,2648201300,1741559704,1736504117,1749615552,1230914153,1841881793,2263972354,1640364052,1718983602,2591956307,1435884942,1113519487,1645804857,1618010182,2319864160,1355610915,2809249360,2525896070,1632016961,1655509117,1653123814,1822554773,1655038093,1956344812,1859409827,1654653060,1401880315,1650611917,1693141730,1747669411,1228403135,1404428511,1791934913,1894273912,2676787155,2013504842,1657706754,2702919953,1085880554,1191258123,1922916485,1169699184,2205823954,2660910161,1914339764,2007346185,1703473342,2286735527,2002566201,1432848814,2195754921,1577826897,1842019903,2185033444,1642191490,1632096922,2143669027,1998855810,2486681311,2319192372,2142166543,1686838273,2192582404,2164354857,1948525413,1654631180,2084774323,1829806063,1767657282,1882794804,1935002392,1134424202,1928074101,1194991743,1646952317,1802456783,1710406277,1804559491,1896402207,1737085310,1426858784,2190468843,2137167015,1408543664,1895407123,1887937931,2340891172,2022496627,2273229020,2251954824,1254576325,1706396283,1961352685,1400037183,1893445411,1980786697,1931895312,2129463470,1642272425,2519623500,2278730467,1261848117,1937618377,2382010265,1586474194,1882579600,1773899833,1344290265,1257917072,1669160941,1966969745,2152024140,1912273717,1723577920,1851507551,1729672055,1735853695,2338558301,2101039025,1277326265,1734650687,1409909551,1949201102,1646856827,2123208787,1863840852,1436804993,1964435393,1648544895,1739930423,1871689107,1035347080,1880324342,2451077552,2430739850,2394848973,1223056620,1831607867,1718500504,1636190514,1836483953,1736332374,2272937850,1461892242,1840195061,1771804151,1408419881,1159342364,1409776524,2308256587,2112822270,1837013461,2317085334,2049142734,1400681091,2299645037,1739533844,1728741887,1970441905,2019264715,1952009671,1712755352,1401356861,1698810635,1404640403,2049209781,1764078023,1753062057,1659260895,1674652552,1703318564,1737103017,1895183737,1996741087,1736171091,2153807481,1802746163,1641544291,2134671703,1223497002,1245241165,1776410887,1735265290,1037030872,1854283601,1646360305,1825469611,1796099013,1689036934,1880601642,1652346893,1714425280,1092413824,1778332085,1939925712,1668145620,1639738335,1483500601,1919243167,1657381930,1764074447,1807883337,1739203352,1219235912,1808067361,1885305177,1893373231,1895296900,1640352340,1675146863,1773304182,1433048232,1688161242,1935465345,1823448493,1670097713,1736378260,1404714514,1839984173,1818500633,1238978035,1844203473,1262574743,1922695813,1923406437,1679395270,1853783333,1642270417,1822779365,1858725494,1650623755,1495290014,1772689277,1253661165,1783781613,1887351955,1830102627,1582459022,1691880813,1734579235,1845955540,1590512961,1874260713,1686919791,1194774797,1275710083,1317810934,1907082055,1873625985,1855055407,1696645563,1074875481,1418078783,1494888412,1881606632,1456899500,1880225897,1643101500,1680260232,1312412824,1852131595,1278777010,1443371104,1197161814,1775597921,1363193441,1888765061,1443090767,1401758270,1684953923,1832797203,1759463991,1424038085,1886030421,1712737737,1829948001,1714153930,1681615287,1643179744,1654619934],"next_cursor":0,"previous_cursor":0,"total_number":399}'
    #windwild_ana(follow_string)
    vip_filter(follow_string)


def export():
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql='SELECT uid,pr,`out` FROM `people_rank4` where flag < 2 order by pr desc'
    cur.execute(sql)
    results = cur.fetchall()
    con.close()
    fp = open('myy.txt','w')
    for result in results:
        fp.write(str(result[0])+','+str(result[1])+','+str(result[2])+'\n')
    fp.close()
    
if __name__ == '__main__':
    print "hello windwild"
    export()
    #method01()
    
    