# Rolling-Update_by_openresty

基于openresty的滚动更新实现

## 介绍

在运维工作中经常会遇到临时上线，如果情况紧急的话，可能在白天也要上，若不能实现滚动更新，用户的体验就会大打折扣。在更新的过程中，不乏数据丢失、链接无效、404、502等错误

当然基于容器编排k8s的滚动更新很容易实现，现状是很多公司还没有使用容器，针对传统部署的应用的滚动更新让用户无感知的这种需求，在大家对用户体验越来越重视的前提下，就显得格外重要

当然网上也有其他方式的实现，我选择openresty的原因是，运维都会拿nginx作为7层负载均衡，用openresty的话就可以在原有业务上做无缝的迁移，也不需要添加新的工具和依赖，只需要把nginx换成openresty

openresty是基于nginx+lua的实现，官网：http://openresty.org/cn/ openresty生态圈很多第三方模块可以使用，并且不必像nginx需要重新编译才能添加新的模块。openresty做好了opm包管理工具，可以直接下载安装

正是结合这些优点, 以openresty为基础，集成基于动态管理upstream里主机列表的功能，用户调用管理upstream的api就可以实现后端real server的上下线。

## Feature

* **openresty是基于nginx+lua的实现，原有nginx的配置无需调整可直接使用，无缝迁移**
* **无需openresty以外的服务，存储使用内存**
* **通过balancer_by_lua_block实现upstream中real server的可管理性，字典化**
* **自己可很方便的实现管理内存中共享字典管理的api**
* **标准的api实现，方便通过shell或python去调用管理upstream的api**
* **在生产环境已经使用一年多，稳定性没问题**

## Docs

[基于cookie后端一致性绑定的逻辑]

![image][https://github.com/327101303/Rolling-Update_by_openresty/blob/master/%E5%9F%BA%E4%BA%8Ecookie%E7%94%A8%E6%88%B7%E8%AE%BF%E9%97%AE%E5%90%8E%E7%AB%AF%E4%B8%80%E8%87%B4%E6%80%A7%E7%BB%91%E5%AE%9A/sticky.png]

