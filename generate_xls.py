# -*- coding:utf-8 -*- 
#!/usr/bin/env python
import MySQLdb
import urllib2
import urllib
import json
import xlwt
import xlrd
from xlutils.copy import copy
import os

listenserver='http://localhost:10010'
checkStatus = {0:"不通过",1:"通过"}
issueStatus = {0:"未发放",1:"正在发放",2:"已到账"}
xlsFile = '/home/work/lico/coinissue/coinIssue.xls'
userindex = '/home/work/lico/coinissue/userindex.txt'
xlsindex = '/home/work/lico/coinissue/xlsindex.txt'

def connect_mysql():
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': 'yqtc',
        'db': 'act214_test'
    }
    c = MySQLdb.connect(**db_config)
    return c

def xlsHeader():
    if os.path.exists(xlsFile) == False:
        xls = xlwt.Workbook(encoding = 'utf8') 
        table = xls.add_sheet("代币分发")
        table.write(0,0,'用户id')
        table.write(0,1,'用户昵称')
        table.write(0,2,'用户钱包地址')
        table.write(0,3,'应发代币数')
        table.write(0,4,'对账状态')
        table.write(0,5,'发放状态')
        xls.save(xlsFile)
    else:
        print 'file:%s exits' % xlsFile

def xlsWrite(row,uid,nick,wallet,coin,cstatus,istatus):
    xls = xlrd.open_workbook(xlsFile)   
    nxls = copy(xls)
    coinsheet = nxls.get_sheet(0)
    coinsheet.write(row,0,uid)
    unick = unicode(nick, "utf-8") 
    coinsheet.write(row,1,unick)
    coinsheet.write(row,2,wallet)
    coinsheet.write(row,3,coin)
    ucstatus = unicode(cstatus,'utf-8')
    coinsheet.write(row,4,ucstatus)
    uistatus = unicode(istatus,'utf-8')
    coinsheet.write(row,5,uistatus)
    nxls.save(xlsFile)

def readIndexFile(filename):
    with open(filename,'r') as f:
       i = f.read()
       if i == "":
           i='0'
    f.close()
    return int(i)

def writeIndexFile(i,filename):
    with open(filename,'w') as f:
       f.write(str(i))
    f.close() 

def check_usercoin(conn,userid):
    sql_getuserdata = 'select F_id,F_nickname,F_wallet_address,F_youcoin,F_issue_status from t_214_user where F_id = %s' % userid
    
    cur = conn.cursor()
    count = cur.execute(sql_getuserdata) 
    
    if count == 0:
        return 
        
    res = cur.fetchone() 

    sql_wit_reward = 'select F_reward from t_214_witness where F_userid = %d' % res[0]
    sql_wit_creator = 'select F_creator_reward from t_214_witness where F_creator_id = %d' % res[0]
    
    cur.execute(sql_wit_reward)
    ret_wit = cur.fetchall()

    wit_reward = 0
    for wt in ret_wit:
        wit_reward += wt[0]

    cur.execute(sql_wit_creator) 
    ret_witcreator = cur.fetchall() 

    wit_creatorreward = 0
    for wtcr in ret_witcreator:
        wit_creatorreward += wtcr[0]
        
        
    sql_queryletter = 'select count(1) from t_214_letter where F_from_id = %d' % userid
    cur.execute(sql_queryletter)
    
    lettercount = cur.fetchone() 
    
    print 'user :%d wit reward :%d crewar :%d letterreward :%d' % (userid , wit_reward , wit_creatorreward , lettercount[0] * 10)
    
    if wit_creatorreward + wit_reward + lettercount[0] * 10 == res[3]:
        return res[0],res[1],res[2],res[3],checkStatus[1],issueStatus[res[4]]
    
    return res[0],res[1],res[2],res[3],checkStatus[0],issueStatus[res[4]]
    


def usercoin_issue(conn,userid,xlsid):

    t_uid = userid
    t_xid = xlsid
    limit = 10
    while True:
        print 't_uid :%d t_xid :%d' % (t_uid,t_xid)
        sql_getuserid = 'select F_id from t_214_user where F_id > %d limit %d' % (t_uid,limit)
        cur = conn.cursor()

        cur.execute(sql_getuserid)
        res = cur.fetchall()

        total = len(res)
        print 'get user total %d' % total
        if total == 0:
            break
         
        
        for u in res:
            uid,nick,wallet,coin,checkstatus,issuestatus = check_usercoin(conn,u[0])
            t_xid += 1
            xlsWrite(t_xid,uid,nick,wallet,coin,checkstatus,issuestatus) 

        t_uid = res[total-1][0]
        writeIndexFile(t_xid,xlsindex)
        writeIndexFile(t_uid,userindex)
        
        if total != limit:
            print 'get data done total:%d' % total
            break
        
        
#    while index < total:
#        print 'index:%d limit:%d' % (index,limit)
#
#        body = {"index":index,"limit":limit}
#        post = json.JSONEncoder().encode(body)
#        request = urllib2.Request('%s/action_214/blockchain/coin_issue' % listenserver, post)
#        request.add_header('Content-type','application/json')
#
#        response = urllib2.urlopen(request)
#        index += limit

    return 

def test_httpreq():
   ind = 15
   limit = 2
   body = {"index":ind,"limit":limit}
   post = json.JSONEncoder().encode(body)
   request = urllib2.Request('http://localhost:10010/action_214/blockchain/letter_onchain', post)
   request.add_header('Content-type','application/json')

   response = urllib2.urlopen(request)
   print response.read()
    

if __name__ == '__main__':
    c = connect_mysql()              # 首先连接数据库

    #test_httpreq() 
    #usercoin_issue(c)
    #xlsHeader() 
    xlsid = readIndexFile(userindex)
    userid = readIndexFile(xlsindex)
    usercoin_issue(c,userid,xlsid)
    c.close()                    # 最后记得关闭数据库连接
