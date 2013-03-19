#coding=utf-8

import urllib2,urllib
import simplejson
import time,re,string
import cookielib


def getWord(seachstr):
    seachstr = urllib.quote(seachstr)

    fault = 0
    ret = 0
    url = ('https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s') % (seachstr)
    # print url
    request = urllib2.Request(url, None, {'Referer': 'http://github.windwild.net'})
    while(fault < 3):
        response = urllib2.urlopen(request)
        try:
            results = simplejson.load(response)
            if(0 == len(results['responseData']['results'])):
                return 0
            eta = results['responseData']['cursor']['resultCount']
            p = re.compile(',')
            eta = re.sub(p,'',eta)
            ret = int(eta)

        except:
            if int(results['responseStatus']) == 403:
                print "meet 404"
                time.sleep(10)
            fault += 1
            continue

        return ret

def getWord2(seachstr):
    seachstr = urllib.quote(seachstr)

    fault = 0
    ret = 0
    url = 'http://www.google.com.hk/search?sourceid=chrome&;ie=UTF-8&q=%s'%(seachstr)
    cj = cookielib.CookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
    opener.addheaders = [('User-agent', 'Opera/9.23')] 
    urllib2.install_opener(opener) 
    req=urllib2.Request(url) 
    response =urllib2.urlopen(req)
    content = response.read()
    p = re.compile("約有(.*?)項結果")
    ret = re.findall(p,content)
    if(len(ret) > 0):
        p = re.compile(',')
        ret = re.sub(p,'',ret[0])
        return int(ret)
    else:
        return 0;

def get_score(n1,n2,n1a2,n1o2):
    n = 1.0*(n1a2*(n1+n2+2*n1a2))/(n1*n2)/4
    return n

def get_relation(word1,word2):
    query_or = '"%s" OR "%s"' % (word1,word2)
    query_and = '"%s" "%s"' % (word1,word2)
    query_word1 = '"%s"' % (word1)
    query_word2 = '"%s"' % (word2)

    fun = getWord2

    n1 = fun(query_word1)
    time.sleep(0.5)
    n2 = fun(query_word2)
    time.sleep(0.5)
    n1a2 = fun(query_and)
    time.sleep(0.5)
    n1o2 = fun(query_or)

    n = get_score(n1,n2,n1a2,n1o2)
    if(n > 1.0):
        n = 1
    return (n,n1,n2,n1a2,n1o2)

def main():
    tests = []
    tests.append(("中国","共产党"))
    tests.append(("Irwin King","CUHK"))
    tests.append(("马云","阿里巴巴"))
    tests.append(("哈工大","哈尔滨工业大学"))

    for test in tests:
        print test[0],test[1], get_relation(test[0],test[1])
        time.sleep(1)


if __name__ == '__main__':
    main()