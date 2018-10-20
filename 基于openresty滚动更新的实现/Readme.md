# 基于openresty的滚动发布功能
# openresty 配置中lua内容
#### nginx.conf配置中定义两个接口

upstream用于获取当前upstream的状态

set_ups用于设置指定upstream下realserver的上下线状态


## sticky
#### 由于stciky模块太久没有更新，和openresty是否兼容的不确定性，
基于balance_by_lua和lua_shared_dict、lua-upstream-nginx-module,实现nginx第三方模块sticky的基于cookie绑定后端realserver的功能


# 使用python发起http get请求，执行下线，部署，上线的过程