#!/usr/bin/env python
# -*- coding:utf-8  -*-
# 把只读的url按行写入本脚本同级目录下的rule.conf中
#通过逐行读取按指定规则，写入配置文件
'''
= 开头表示精确匹配
^~ 开头表示uri以某个常规字符串开头
~  开头表示区分大小写的正则匹配
~* 开头表示不区分大小写的正则匹配
!~和!~* 分别为区分大小写不匹配 以及 不区分大小写不匹配的正则
/  通用匹配，任何请求都会匹配到，优先级最低
'''

import nginx

c = nginx.loadf('base.conf')

s = c.servers[1]
# count_location = s.locations.__len__()
# print count_location

def Location_Add(arg):
    s.add(
        nginx.Location(arg,
            nginx.Key('proxy_set_header','X-Real-IP  $remote_addr'),
            nginx.Key('proxy_pass', 'http://readonly'),
            nginx.Key('proxy_redirect','off'),
            )
        )



if __name__ == '__main__':
    with open('rule.list', 'r') as f:
        for n in f.readlines():
            print n.strip()
            Location_Add(n.strip())

    nginx.dumpf(c, 'temp.conf')