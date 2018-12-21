#-*- coding: utf-8 -*-

import sys,re,time, datetime
import random
import urllib2
import json
import MySQLdb
from scrapy.selector import Selector
import cookielib
from CONFIG import MYSQL_DB_HOST, MYSQL_DB_USER, MYSQL_DB_NAME, MYSQL_DB_PASS, MYSQL_DB_PORT
reload(sys)
sys.setdefaultencoding('utf-8')

def parse(html,url):
    sel=Selector(text=html)
    num = len(sel.xpath("//*[@id='coupons-list']//@data-key"))
    if num < 1:
        print u'抓取结束！'
        sys.exit()

    path=[]
    batchs=[]
    keys=[]
    for i in range(1,num+1,1):
        temp_path="//*[@id='coupons-list']/div["+str(i)+"]"
        path.append(temp_path)
        batch_elem = sel.xpath(temp_path+'/div[1]/div[@class="q-range"]//@coupon-time').extract()
        key=sel.xpath(temp_path+'/@data-key').extract()
        if len(batch_elem) > 0 :
            keys.append(''.join(key))
            batchs.append(''.join(batch_elem))
        else:
            print 'Error: batch elem not found!'
            continue
    if len(batchs) < 1:
        print 'Error: no valid batchs found, scrapy failed!'
        return False

    req=urllib2.Request('http://a.jd.com/batchTime.html?batchId='+'&batchId='.join(batchs),headers=headers)
    response=urllib2.urlopen(req,timeout=10)
    batchTime=json.loads(response.read())

    #login required, Deprecated: http://a.jd.com/ajax/queryGotActs.html
    req=urllib2.Request('http://a.jd.com/ajax/queryActsStatus.html?r='+str(random.random())+'&acData%5B%5D='+'&acData%5B%5D='.join(keys),headers=headers)
    response=urllib2.urlopen(req,timeout=10)
    acData=json.loads(response.read())
    if len(acData['data']) > 0:
        acData = { i['ruleId']:i for i in acData['data'] }
    else:
        print(u'Error: empty acData dict, failed to query nextTime from JD api.')

    for i in range(0,len(batchs),1):
        id=sel.xpath(path[i]+'/@id').extract()
        id=''.join(id).strip()
        keyurl=sel.xpath(path[i]+'/@data-key').extract()
        useurl=sel.xpath(path[i]+'/@data-linkurl').extract()
        reduction=sel.xpath(path[i]+'/div[1]/div[1]/strong/text()').extract()
        type=sel.xpath(path[i]+'/div[1]/div[1]/div/div[1]/text()').extract()
        payment=sel.xpath(path[i]+'/div[1]/div[@class="limit"]/span/text()').extract()
        condition=sel.xpath(path[i]+'/div[1]/div[@class="q-range"]/div[1]/p/text()').extract()
        platform=sel.xpath(path[i]+'/div[1]/div[@class="q-range"]/div[2]/text()').extract()
        platform=''.join(platform).replace('\n','').strip()
        batchid=sel.xpath(temp_path+'/div[1]/div[@class="q-range"]//@coupon-time').extract()
        batchid=''.join(batchid).replace('\n','').strip()
        try:
            platform[0]
        except:
            platform=sel.xpath(path[i]+'/div[1]/div[2]/div[2]/p/text()').extract()
        #time=sel.xpath(path[i]+'/div[1]/div[2]/div[3]/text()').extract()
        time=batchTime[batchid]

        try:
            pattern=re.compile('\d{1,5}')
            match=pattern.search(''.join(payment).strip())
            pay=match.group(0)
        except:
            #无限额
            pay='0'
            
        pattern=re.compile(r'.*(?=-)')
        match=pattern.search(''.join(time).strip())
        if match==None:
            print u'获取完成'
        try:
            start_time=match.group(0)
            pattern=re.compile('(?<=-).*')
            match=pattern.search(time.strip())
            end_time=match.group(0)
        except:
            start_time=''
            end_time=''
            pass;
        if keyurl!=[]:
            keyurl='http://a.jd.com/ajax/freeGetCoupon.html?key='+keyurl[0]
        else:
            keyurl='需要京豆兑换'

        option={'status':-1, 'nextTime': -1}
        if id.replace('_a', '') in acData:
            option=acData[id.replace('_a', '')]

        value=[]
        value.append(id)
        value.append(''.join(reduction).strip())
        value.append(''.join(keyurl).strip())
        value.append(batchid)
        value.append(''.join(useurl).strip())
        value.append(''.join(pay).strip())
        value.append(''.join(condition).strip())
        value.append(''.join(platform).strip())
        value.append(''.join(type).strip())
        value.append(start_time)
        value.append(end_time)
        value.append(url)

        if value[5]!='0':
            discount=float(value[5])-float(value[1])
            percent=round(float(discount)/float(value[5]),3)
        else:
            discount=float(value[1])
            percent=float(0)
        value.append(discount)
        value.append(percent)

        value.append(option['status'])
        value.append(datetime.datetime.fromtimestamp(option['nextTime'] / 1e3).strftime("%Y-%m-%d %H:%M:%S"))

        selectsql="select id from jd_discount_self where id="+"'"+value[0]+"'"
        try:
            count=cur.execute(selectsql)
            if count==0:
                sql='insert into jd_discount_self(id,reduction,get_url,batchid,used_url,payment,requirement,platform,coupon_type,starttime,endtime,url,discount,percent,status,nexttime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            else:
                sql='update jd_discount_self set reduction=%s,get_url=%s,batchid=%s,used_url=%s,payment=%s,requirement=%s,platform=%s,coupon_type=%s,starttime=%s,endtime=%s,url=%s,discount=%s,percent=%s,status=%s,nexttime=%s WHERE id=%s'
                del value[0]
                value.append(id)
            cur.execute(sql,value)
            conn.commit()
        except Exception as e:
            print u"Mysql Error: %s" % (e)

baseurl='http://a.jd.com/coupons.html?page='
url=[]
for i in range(0,100,1):
    url_tmp=baseurl+str(i)+'&ct=4&st=2'
    url.append(url_tmp)
cookie=cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)
headers={'Host':'a.jd.com',
    'User-Agent':'Mozilla/5.0(WindowsNT6.3;WOW64;rv:47.0)Gecko/20100101Firefox/47.0',
    'Accept':'application/json,text/javascript,*/*;q=0.01',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'X-Requested-With':'XMLHttpRequest',
    'Referer':'http://a.jd.com/coupons.html',
    'Connection':'keep-alive'}
try:
    conn=MySQLdb.connect(host=MYSQL_DB_HOST,user=MYSQL_DB_USER,passwd=MYSQL_DB_PASS,db=MYSQL_DB_NAME,port=MYSQL_DB_PORT)
    cur=conn.cursor()
    conn.set_character_set('utf8')
except MySQLdb.Error,e:
    print u"Mysql Error %d: %s" % (e.args[0], e.args[1])
    
for i in range(0,len(url),1):
    time.sleep(1)
    req=urllib2.Request(url[i],headers=headers)
    response=urllib2.urlopen(req,timeout=10)
    parse(response.read(),url[i])
    print u'爬取第'+str(i+1)+'页成功'
cur.close()
conn.close()

