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
import copy

def get_item_array(results):
    array = []
    for item in results:
        array.append(item[0])
    return array

def get_item_string(array):
    return_string = ""
    for item in array:
        return_string = return_string + str(item) + ","
    return return_string[:-1]

def select_data_set(x_lim,y_lim):
    con = mdb.connect('localhost','root','root','weibo_ranker')
    cur = con.cursor()
    sql = "select uid from people_rank4 where flag = 0 order by pr desc limit %d"%(x_lim)
    cur.execute(sql)
    items = cur.fetchall()
    item_array = get_item_array(items)
    item_string = get_item_string(item_array)
    
    sql = "select uid from people_rank4 where pr>1 and pr<5 and `out` > 300 and `out`< 500 order by pr limit %d"%(y_lim)
    cur.execute(sql)
    users = cur.fetchall()
    user_array = get_item_array(users)
    user_string = get_item_string(user_array)
    
    sql = "select * from (select * from vip_relation where `to` in (%s)) as res1 where `from` in (%s)"%(item_string,user_string)
    cur.execute(sql)
    relations = cur.fetchall()
    
    relation_array = []
    for relation in relations:
        relation_array.append((relation[0],relation[1]))
    fp = open("data.txt",'w')
    fp.write(item_string+"\n")
    fp.write(user_string+"\n")
    for relation in relation_array:
        fp.write("%d,%d\n"%(relation[0],relation[1]))
    fp.close()
    con.close()
    

def matrix_factorisation(R, K, steps=1000, alpha=0.0005, beta=0.02):
    N = len(R)
    M = len(R[0])
    P = np.random.rand(N,K)
    Q = np.random.rand(M,K)
    
    Q = Q.T
    for step in xrange(steps):
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - np.dot(P[i,:],Q[:,j])
                    for k in xrange(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = np.dot(P,Q)
        e = 0
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - np.dot(P[i,:],Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[i][k],2) + pow(Q[k][j],2))
        print step
        if e < 0.001:
            break

    return P, Q.T, e

    
def load_data2(x_lim,y_lim):
    fp = open("data.txt",'r')
    item_string = fp.readline()[:-1]
    user_sting = fp.readline()[:-1]
    item_array = item_string.split(',')
    #print item_array
    user_array = user_sting.split(',')
    #print user_array
    #relation_matrix = [[0.0] * x_lim] * y_lim
    relation_matrix = [[0.0 for col in range(x_lim)] for row in range(y_lim)] 
    progress = 1
    for i in range(x_lim * y_lim):
        str = fp.readline()[:-1]
        if str == "" :
            break
        a,b = str.split(',')
        x = item_array.index(b)
        y = user_array.index(a)
        relation_matrix[y][x] = 1.0
    print "density:",1.0*i/(x_lim*y_lim)
    return relation_matrix
    
def remove_random(relation_matrix,rate=0.1):
    y_lim = len(relation_matrix)
    x_lim = len(relation_matrix[0])
    test_matrix = [[0.0 for col in range(x_lim)] for row in range(y_lim)] 
    for y in range(y_lim):
        for x in range(x_lim):
            if(relation_matrix[y][x] != 0):
                if(np.random.random() > 1.0 - rate):
                    pre = relation_matrix[y][x]
                    relation_matrix[y][x] = 0.0
                    test_matrix[y][x] = pre
    return test_matrix
                    

def NMF_weibo(x_lim=50, y_lim=1000, steps = 100, k = 2, alaph = 0.001, sample_rate = 0.1):
    select_data_set(x_lim,y_lim)
    relation_matrix = load_data(x_lim,y_lim)
    relation_matrix_pre = copy.deepcopy(relation_matrix)
    removed_array = remove_random(relation_matrix,sample_rate)
    print "inited"
    u, v, e = matrix_factorisation(relation_matrix,k,steps,alaph)
    print "done"
    predict = np.dot(u, v.T)
    e = 0.0
    for item in removed_array:
        e += pow(predict[item[0]/x_lim][item[0]%x_lim] - item[1],2)
    return e/len(removed_array)



def test_NMF_weibo(x_lim=50, y_lim=1000, steps = 2048, k = 2, alaph = 0.001, sample_rate = 0.1):
    select_data_set(x_lim,y_lim)
    relation_matrix = load_data2(x_lim,y_lim)
    relation_matrix_pre = copy.deepcopy(relation_matrix)
    test_matrix = remove_random(relation_matrix,sample_rate)
    
    print "inited"
    matrix_factorisation_2(relation_matrix,k,steps,alaph,test_matrix=test_matrix,filename="NMF_WEIBO_RESULT.txt")

def load_data(path,x_lim,y_lim):
    rate_matrix =  [[0 for col in range(x_lim)] for row in range(y_lim)]
    fp = open(path,'r')
    max_u,max_i = 0,0
    for line_num in range(100000):
        line = fp.readline()
        if(line ==''): break
        user,item,rate,time = line.split()
        user,item,rate = int(user),int(item),int(rate)
        rate_matrix[user-1][item-1] = rate
    return rate_matrix

    
def NMF_ML():
    x_lim,y_lim = 1682,943
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.base"
    rate_matrix = load_data(path,x_lim,y_lim)
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.test"
    test_matrix = load_data(path,x_lim,y_lim)
    print "inited"
    u,v,e1 = matrix_factorisation(rate_matrix,2,10,0.001)
    predict = np.dot(u, v.T)
    e2 = 0.0
    counter = 0
    for i in range(x_lim*y_lim):
        if(test_matrix[i/x_lim][i%x_lim] != 0):
            counter += 1
            e2 += pow(test_matrix[i/x_lim][i%x_lim] - predict[i/x_lim][i%x_lim] , 2)
    e2 = e2/counter
    print e2

def matrix_factorisation_2(R, K, steps=1000, alpha=0.0005, beta=0.02, test_matrix=[],filename="result.txt"):
    fp = open(filename,'w+')
    N = len(R)
    M = len(R[0])
    P = np.random.rand(N,K)
    Q = np.random.rand(M,K)
    
    Q = Q.T
    for step in xrange(steps):
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - np.dot(P[i,:],Q[:,j])
                    for k in xrange(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = np.dot(P,Q)
        e = 0
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - np.dot(P[i,:],Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[i][k],2) + pow(Q[k][j],2))
        
        predict = np.dot(P, Q)
        e2 = get_error_rate(predict,test_matrix,M,N)
        print step, e2
        fp.write("%d,%f\n"%(step,e2))
        if e < 0.001:
            break
    fp.close()
    return P, Q.T, e
    
def get_error_rate(predict,test_matrix,x_lim,y_lim):
    e = 0.0
    counter = 0
    for i in range(x_lim*y_lim):
        if(test_matrix[i/x_lim][i%x_lim] != 0):
            counter += 1
            e += pow(test_matrix[i/x_lim][i%x_lim] - predict[i/x_lim][i%x_lim], 2)
    e = e/counter
    return e
    
    

def test_NMF_ML():
    x_lim,y_lim = 1682,943
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.base"
    rate_matrix = load_data(path,x_lim,y_lim)
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.test"
    test_matrix = load_data(path,x_lim,y_lim)
    fp = open('NMF_ML_result.txt','w')
    print "inited"
    matrix_factorisation_2(rate_matrix,5,2048,0.001,test_matrix=test_matrix,filename="NMF_ML_result_5.txt")
    
    
def pcc(row1,row2):
    if(len(row1) != len(row2)): return 0.0
    size = len(row1)
    sum,counter = 0,0
    
    for i in range(size):
        if(row1[i] != 1):
            counter += 1
            sum += row1[i]
    ave1 = 1.0 * sum / counter
    
    for i in range(size):
        if(row2[i] != 1):
            counter += 1
            sum += row2[i]
    ave2 = 1.0 * sum / counter
    
    upper = 0.0
    for i in range(size):
        if(row1[i] != 0 and row2[i] != 0):
            upper += (row1[i] - ave1)*(row2[i] - ave2)
    
    left,right = 0.0,0.0
    for i in range(size):
        if(row1[i] != 0 and row2[i] != 0):
            left += (row1[i]-ave1)**2
            right += (row2[i]-ave2)**2
    return upper/((left**0.5)*(right**0.5))
    
def consine(row1,row2):
    if(len(row1) != len(row2)): return 0.0
    size = len(low1)
    upper = 0.0
    lower = 0.0
    for i in range(size):
        upper += row1[i] * row2[i]
        left += row1[i]**2
        right += row2[i]**2
    return upper/((left**0.5)*(right**0.5))
    
def kNN(k=10):
    x_lim,y_lim = 1682,943
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.base"
    rate_matrix = load_data(path,x_lim,y_lim)
    path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.test"
    test_matrix = load_data(path,x_lim,y_lim)
    ave_arr = []
    
    pcc_arr = [[0.0 for col in range(x_lim)] for row in range(y_lim)]
    for i in range(y_lim-1):
        for j in range(i+1,x_lim):
            pcc_v = pcc(rate_matrix[i],rate_matrix[j])
            pcc_arr[i][j] = pcc_v
            pcc_arr[j][i] = pcc_v
    
    for i in range(x_lim):
        counter,sum = 0,0
        for j in range(y_lim):
            if(rate_matrix[j][i] != 0):
                sum += rate_matrix[j][i]
                counter += 1
        if(counter == 0):ave=0
        else: ave = 1.0 * sum / counter
        ave_arr.append(ave)
    
    for i in range(x_lim * y_lim):
        if(test_matrix[i/x_lim][i%x_lim] != 0):
            pass
            
def get_r(rate_matrix,ave_arr,k,user,item,x_lim,y_lim,pcc_arr):
    pcc_list = []
    counter = 0
    for u in pcc_arr[user]:
        pcc_list.append((u,counter))
        counter += 1
   
def auto_test():
    for k in range(1,6):
        x_lim,y_lim = 1682,943
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u%d.base"%(k)
        rate_matrix = load_data(path,x_lim,y_lim)
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u%d.test"%(k)
        test_matrix = load_data(path,x_lim,y_lim)
        try:
            matrix_factorisation_2(rate_matrix,K=2,steps=128,alpha=0.001,test_matrix=test_matrix,filename="results/NMF_ML_result_128_2_u%d.txt"%(k))
        except:
            pass
    
    for k in range(1,6):
        x_lim,y_lim = 1682,943
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.base"
        rate_matrix = load_data(path,x_lim,y_lim)
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.test"
        test_matrix = load_data(path,x_lim,y_lim)
        try:
            matrix_factorisation_2(rate_matrix,K=2,steps=128,alpha=0.0005*k,test_matrix=test_matrix,filename="results/NMF_ML_result_128_alaph%d.txt"%(k))
        except:
            pass
    
    for k in range(1,6):
        x_lim,y_lim = 1682,943
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.base"
        rate_matrix = load_data(path,x_lim,y_lim)
        path = "/Users/windwild/Google Drive/CUHK/DataMining/project/100k/u1.test"
        test_matrix = load_data(path,x_lim,y_lim)
        try:
            matrix_factorisation_2(rate_matrix,K=k,steps=128,alpha = 0.001,test_matrix=test_matrix,filename="results/NMF_ML_result_128_k%d.txt"%(k))
        except:
            pass
    
def gen_pic():
    plt.figure(figsize=(8,4))
    color=['r','g','b','k','y']
    plt.xlabel("steps")
    plt.ylabel("error rate")
    plt.title("Error rate on Weibo Dataset")
    fp = open("results/NMF_WEIBO_result_2.txt",'r')
    x_set,y_set = [],[]
    for j in range(128):
        line = fp.readline()
        if(j<0): continue
        if(line == ""): break
        x,y = line.split()
        x_set.append(x)
        y_set.append(y)
    plt.plot(x_set,y_set,'-',color='b',label="error rate")
    plt.legend()
        
    plt.savefig('NMF_WEIBO.png')
            
    

if __name__ == '__main__':
    gen_pic()
    #auto_test()
    #test_NMF_ML()
    #test_NMF_weibo()
    
    