#!/usr/bin/env python
# -*- coding:utf-8  -*-
'''
第一个版本使用python-nginx模块来修改nginx配置文件然后重载nginx服务。
第二个笨笨使用vst获取realserver的response_total。使用动态管理upstream的模块的api来通过http请求调整realserver的状态。缺点是无法持久化
'''

import nginx,json,commands,time
import  urllib,requests
import paramiko,sys
'''
第一版使用python-nginx模块解析nginx配置文件。跨主机管理会有很多不方便的地方
第二版使用动态upstream管理的第三方模块通过操作api来实现多upstream的调整

'''
class Ssh_Con(object):
    def __init__(self,hostname,port,username,pkey,password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(pkey)
        self.password = password
    def connect(self):
        transport = paramiko.Transport(self.hostname, self.port)
        transport.connect(username=self.username, pkey=self.pkey)
        self.__transport = transport

    def run(self,arg):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = self.__transport
        #当远程连接用户为非root用户时，需要提供sudo切换时，需要的该用户密码
        if self.username != 'root':
            ssh = ssh.invoke_shell()
            time.sleep(0.1)
            ssh.send('su - \n')
            buff = ''
            while not buff.endswith('Password: '):
                resp = ssh.recv(9999)
                buff += resp
            ssh.send(self.password)
            ssh.send('\n')
            buff = ''
            while not buff.endswith('# '):
                resp = ssh.recv(9999)
                buff += resp
            ssh.send(arg)
            ssh.send('\n')
            buff = ''
            while not buff.endswith('# '):
                resp = ssh.recv(9999)
                buff += resp
            # s.close()
            result = buff
        else:
            stdin, stdout, stderr = ssh.exec_command(arg)
            result = stdout.read()
            # s.close()
        print result

    def Close(self):
        self.__transport.close()


'''
# con = Ssh_Con(hostname='ss.shinfo.co',port=22,username='sa',pkey='/Users/junzhang/.ssh/id_rsa',password='zhangjun123')
con = Ssh_Con(hostname='192.168.2.27',port=22,username='sa',pkey='/Users/junzhang/.ssh/id_rsa',password=None)
con.connect()
con.run('ls -l')
con.Close()
'''
nginx_ssh = Ssh_Con(hostname='192.168.2.27',port=22,username='root',pkey='/Users/junzhang/.ssh/id_rsa',password=None)
nginx_ssh.connect()
nginxconf='/etc/nginx/sites-enabled/www.123.com'
c = nginx.loadf(nginxconf)
s_list=[]
u = c.filter('Upstream',name='web')[0]
print u.keys
for n in u.keys:
    s_list.append(n)

print s_list

def get_vst():
    res = requests.get('http://192.168.2.27/vts/format/json')
    m = res.json()["upstreamZones"]['web']
    for n in m:
        if n['down'] == True:
            return n
            # res = m["requestCounter"]

print get_vst()

for n in s_list:
    u.remove(n)
    new_key = nginx.Key(name='server',value='{0} {1}'.format(n.value,'down'))
    u.add(new_key)
    nginx.dumpf(c,nginxconf)
    (status,text)=commands.getstatusoutput('nginx -s reload')
    if status == 0 :
        time.sleep(3)
        res = get_vst()["requestCounter"]
        print 'res:',res
        time.sleep(10)
        new_res = get_vst()["requestCounter"]
        print 'new_res:',new_res
        if new_res == res:
            # pass
            print "可以升级这个实例",n.value
            # 升级
            # sync
            # 验证
            url =   'http://{0}'.format(n.value)
            status = requests.get(url).status_code
            if status == 200 :
                print "升级成功"
                # 放开
                u.remove(new_key)
                u.add(n)
                nginx.dumpf(c, nginxconf)
        else:
            time.sleep(10)
                        # pass
            print "可以升级这个实例",n.value
            # 升级
            # sync
            # 验证
            url =   'http://{0}'.format(n.value)
            status = requests.get(url).status_code
            if status == 200 :
                print "升级成功"
                # 放开
                u.remove(new_key)
                u.add(n)
                nginx.dumpf(c, nginxconf)
        # raw_input('输入任意键继续')
    else:
        print 'nginx重启失败:',text
(status,text)=commands.getstatusoutput('nginx -s reload')
if status == 0:
    print "所有实例升级完成，重载nginx配置"



res = requests.get('www.baidu.com')
res.json


str.strip()