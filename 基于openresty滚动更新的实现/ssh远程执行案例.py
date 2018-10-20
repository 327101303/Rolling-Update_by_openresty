#!/usr/bin/env python
# -*- coding:utf-8  -*-

import paramiko,time
'''
private_key = paramiko.RSAKey.from_private_key_file('/Users/junzhang/.ssh/id_rsa')
transport = paramiko.Transport(('192.168.2.27', 22))
transport.connect(username='root', pkey=private_key)
ssh = paramiko.SSHClient()
ssh._transport = transport
stdin, stdout, stderr = ssh.exec_command('df')
print stdout.read()
transport.close()
'''


class Ssh_Con(object):
    def __init__(self,hostname,port,username,pkey,):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(pkey)
    def connect(self):
        transport = paramiko.Transport(self.hostname, self.port)
        transport.connect(username=self.username, pkey=self.pkey)
        self.__transport = transport

    def run(self,arg):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = self.__transport
        if self.username != 'root':
            ssh = ssh.invoke_shell()
            time.sleep(0.1)
            ssh.send('su - \n')
            buff = ''
            while not buff.endswith('Password: '):
                resp = ssh.recv(9999)
                buff += resp
            ssh.send(123)
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



con = Ssh_Con(hostname='192.168.2.27',port=22,username='root',pkey='/Users/junzhang/.ssh/id_rsa')
con.connect()
con.run('ls -l')
con.Close()