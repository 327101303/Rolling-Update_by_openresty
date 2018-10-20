#!/usr/bin/env python
# -*- coding:utf-8  -*-
import paramiko
import requests
import time



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


def make_dic(text):

    lis = []
    for n in text.split("\n"):
        tmp_list = []
        mid_dic = {}
        for m in  n.lstrip().split(","):
            tmp_dic = {}
            new_list = m.split("=")
            if  len(new_list) != 1:
                tmp_dic[new_list[0].strip()] = new_list[1].strip()
            mid_dic = dict(mid_dic,**tmp_dic)
        if len(mid_dic) != 0:
            lis.append(mid_dic)
    return lis

def get_url(nginx_host):
    url = "http://{0}:8080/upstreams".format(nginx_host)
    return requests.get(url)


def upstream_status(nginx_host):
    res_list = []
    for n in get_url(nginx_host).text.split("upstream")[1:]:
        dic = {}
        s = n.split(":\n")
        s[1]=make_dic(s[1])
        dic[s[0].strip()]=s[1]
        res_list.append(dic)
        # print res_list
    return res_list

def get_host(nginx_host,upstream_name):
    host_list=[]
    for n in upstream_status(nginx_host):
        for k,v in n.items():
            if k == upstream_name:
                for m in v:
                    if m['name'].split(":")[0] not in host_list:
                        host_list.append(m['name'].split(":")[0])
    return host_list
#下线
def offline(host,nginx_host,upstream_name):
    print "{0}主机所有webserver即将下线。".format(host)
    #下线
    #检测conns
    #conns为0时return host
    id_list=[]
    for n in upstream_status(nginx_host):
        for k,v in n.items():
            if k == upstream_name:
                for m in v:
                    if  m['name'].find(host) != -1:
                        id_list.append(m['id'])
                    else:
                        pass
    # print id_list

    for n in id_list:
        print 'http://{0}:8080/set_ups?name={1}&backup=false&id={2}&down=true'.format(nginx_host,upstream_name,n)
        res = requests.get('http://{0}:8080/set_ups?name={1}&backup=false&id={2}&down=true'.format(nginx_host,upstream_name,n))
        if res.text == "true\n":
            print "下线成功\n"
        else:
            print res.text
    return id_list

#检测realserver连接数
def discover_conns(id_list,nginx_host,upstream_name):
    tag = 0
    for id in id_list:
        for n in upstream_status(nginx_host):
            for k, v in n.items():
                if k == upstream_name:
                    for real_server in v:
                        if real_server['id'].find(id) != -1:
                            tag = tag + int(real_server['conns'])
    if tag == 0:
        print "realserver连接已全部断开，可以升级"
        return tag
    else:
        "realserver有连接尚未断开，请等待"
        return tag
#部署
def Deploy(host):
    '''
    try:
        # 同步代码
        # 重启服务
        # 断开连接
        con = Ssh_Con(hostname=host, port=22, username='root', pkey='/Users/junzhang/.ssh/id_rsa', password=None)
        print('---------')
        con.connect()
        # 同步代码
        con.run('cd /opt/ethicall/script && ./02.sync.py.sh')
        con.run('/usr/bin/supervisorctl restart all')
        # con.run('echo {0} >>/tmp/`date +%Y%m%d-%H%M%S`'.format(host))
        con.Close()
        print '部署成功'
        return 0
    except Exception, e:
        print e
        print "执行失败，需人为干预"
        return 1
    '''
    return 0
    pass
#上线
def online(id_list,nginx_host,upstream_name):
    for n in id_list:
        print 'http://{0}:8080/set_ups?name={1}&backup=false&id={2}&down=false'.format(nginx_host,upstream_name,n)
        res = requests.get('http://{0}:8080/set_ups?name={1}&backup=false&id={2}&down=false'.format(nginx_host,upstream_name,n))
        if res.text == "true\n":
            print "上线成功\n"
        else:
            print res.text


def main():
    pass

if __name__ == '__main__':
    nginx_host="192.168.2.34"
    upstream_name='bar'

    host_list = get_host(nginx_host,upstream_name)
    for n in host_list:
        id_list = offline(n,nginx_host,upstream_name)
        while discover_conns(id_list,nginx_host,upstream_name) > 0:
            print "延时3s，等待所有连接断开"
            time.sleep(3)

        else:
            res = Deploy(n)
            if res ==0 :
                online(id_list,nginx_host,upstream_name)
            else:
                print "该主机执行部署失败，需手动干预，"
                break

    # other_host = ['web3','db']
    # for n in other_host:
    #     Deploy(n)
