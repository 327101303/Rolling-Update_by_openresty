#!/usr/bin/env python
# -*- coding:utf-8  -*-


import requests,commands,paramiko
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


def GetServer_list(url):
    res = requests.get(url)
    # res.content
    all_lis = []
    for n in res.content.replace('server ', '').strip().split(';\n'):
        lis =  n.strip(';').split(':')
        dic = {}
        dic[lis[0]]= lis[1]
        # print dic
        all_lis.append(dic)
    print all_lis
    return all_lis

def get_vst():
    res = requests.get('http://192.168.2.27/vts/format/json')
    m = res.json()["upstreamZones"]['backends']
    for n in m:
        if n['down'] == True:
            return n
host_tag = 0
def polling_update(args,nginxhost):
    for n in args:
        for host,bport in n.items():
            print host,bport
            try:
                if host_tag != host and con:
                    con.Close()
                    host_tag = host
                    con = Ssh_Con(hostname=host, port=22, username='root', pkey='/Users/junzhang/.ssh/id_rsa', password=None)
                    print('---------')
                    con.connect()
                    #同步代码
                    con.run('cd /opt/ethicall/script && ./02.sync.py.sh')
                    con.run('echo {0} >>/tmp/`date +%Y%m%d-%H%M%S`'.format(host))
            except Exception,e:
                print e
                con = Ssh_Con(hostname=host, port=22, username='root', pkey='/Users/junzhang/.ssh/id_rsa', password=None)
                print('----')
                con.connect()
                host_tag = host
                #同步代码
                con.run('cd /opt/ethicall/script && ./02.sync.py.sh')
                con.run('echo {0} >>/tmp/`date +%Y%m%d-%H%M%S`'.format(host))



            #下线
            # curl "http://127.0.0.1/dynamic?upstream=zone_for_backends&server=127.0.0.1:8000&down="
            url = 'http://{3}/dynamic?upstream=zone_for_backends&server={0}:{1}&down='.format(host,bport,nginxhost)
            print url
            res = requests.get(url)
            if res.status_code == 200:
                #等待可以升级的状态
                res = 0
                new_res =1
                while new_res != res:
                    res = get_vst()["requestCounter"]
                    print 'res:', res
                    time.sleep(5)
                    new_res = get_vst()["requestCounter"]
                    print 'new_res:', new_res
                    # time.sleep(5)


                #重启
                # con = Ssh_Con(hostname=host, port=22, username='root', pkey='/Users/junzhang/.ssh/id_rsa',password=None)
                # print "(status,text) = commands.getstatusoutput('supervisorctl restart ethicall_{0}'.format(bport[2]))"
                con.run('supervisorctl restart ethicall_{0}'.format(bport[2]))
                # con.run('docker restart w{0}'.format(bport[2]))
                #验证
                time.sleep(5)
                if requests.get('http://{0}:{1}'.format(host,bport)).status_code == 200:
                    #上线
                    if requests.get(url.replace('down','up')).status_code == 200:
                        print "该实例上线成功"
                        pass
                    else:
                        print "该实上线失败"
                else:
                    print '该实例启动失败'
            else:
                print res.status_code
    con.Close()
def update_celery(args):
    con = Ssh_Con(hostname=args, port=22, username='root', pkey='/Users/junzhang/.ssh/id_rsa', password=None)
    con.connect()
    #同步代码
    con.run('cd /opt/ethicall/script && ./02.sync.py.sh')
    #重启实例
    con.run('supervisorctl restart all')
    con.Close()

if __name__ == '__main__':
    url = 'http://192.168.2.27/dynamic?upstream=zone_for_backends'
    lis = GetServer_list(url)
    lis.append(['db','48069'])
    nginxhost = 'nginx'
    polling_update(lis,nginxhost)
    update_celery('web3')