lua_shared_dict cache 5m;

upstream product{
         server   192.168.10.95:48169  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.95:48269  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.95:48369  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.95:48469  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.95:48569  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.95:48669  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.94:48169  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.94:48269  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.94:48369  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.94:48469  weight=5 max_fails=2 fail_timeout=30s;
         server   192.168.10.94:48569  weight=5 max_fails=2 fail_timeout=30s;
    balancer_by_lua_block {
    local balancer = require "ngx.balancer"
    local upstream = require "ngx.upstream"
    local upstream_name = 'product'
    local srvs = upstream.get_servers(upstream_name)
    function get_server()
        local cache = ngx.shared.cache
        local key = "req_index"
        local index = cache:get(key)
        if index == nil or index > #srvs then
            index = 1 cache:set(key, index)
        end
        cache:incr(key, 1)
        return index
        end
    function is_down(server)
        local down = false
        local perrs = upstream.get_primary_peers(upstream_name)
        for i = 1, #perrs do
            local peer = perrs[i]
            if server == peer.name and peer.down == true then
                down = true
            end
        end
        return down
    end
    ----------------------------
    local route = ngx.var.cookie_route
    local server
    if route then
        local flag
        for k, v in pairs(srvs) do
            if ngx.md5(v.name) == route then
                server = v.addr
                local flag = 1
                --ngx.log(ngx.INFO,'server0:',server)
            end
        end
        --检测当server下线状态和cooike不匹配的情况
        if is_down(server) or flag == nil  then
            --ngx.log(ngx.INFO,'server01:',server)
            route = nil
        end
    end
    if not route then
        for i = 1, #srvs do
            if not server or is_down(server) then
                server = srvs[get_server()].addr
            end
        end
        --ngx.log(ngx.INFO,'server1:',server)
        local expires = 3600 * 24  -- 1 day
        ngx.header["Set-Cookie"] = 'route=' .. ngx.md5(server) .. '; path=/;Expires=' .. ngx.cookie_time(ngx.time() + expires )
    end
        --ngx.log(ngx.INFO,'server2:',server)
    local index = string.find(server, ':')
    local host = string.sub(server, 1, index - 1)
    local port = string.sub(server, index + 1)
    balancer.set_current_peer(host, tonumber(port))
    }
}
server {
        listen 8080;

	access_log /var/log/nginx/admin.log;
	error_log /var/log/nginx/admin_error.log;
        location = /upstreams {
            default_type text/plain;
            content_by_lua_block {
                local concat = table.concat
                local upstream = require "ngx.upstream"
                local get_servers = upstream.get_primary_peers
                local get_upstreams = upstream.get_upstreams
                local get_primary = upstream.get_primary_peers

                local us = get_upstreams()
                for _, u in ipairs(us) do
                    ngx.say("upstream ", u, ":")
                    local srvs, err = get_servers(u)
                    if not srvs then
                        ngx.say("failed to get servers in upstream ", u)
                    else
                        -- ngx.say(type(srvs))
                        for _, srv in ipairs(srvs) do
                            local first = true
                            for k, v in pairs(srv) do
                                if first then
                                    first = false
                                    ngx.print("    ")
                                else
                                    ngx.print(", ")
                                end
                                if type(v) == "table" then
                                    ngx.print(k, " = {", concat(v, ", "), "}")
                                else
                                    ngx.print(k, " = ", v)
                                end
                            end
                            ngx.print("\n")
                        end
                    end
                end
            }
          }

        location /set_ups{
            default_type text/plain;
            content_by_lua_block {
                local upstream = require "ngx.upstream"
                local getArg = ngx.req.get_uri_args()
                local upstream_name = getArg['name']
                local is_backup = getArg['backup']
                local peer_id = getArg['id']
                local down_value = getArg['down']
                function swap(key)
                    if key  == 'true' then
                        key=true
                        return key
                    elseif key  == 'false' then
                        key=false
                        return key
                    end
                end
                local is_backup = swap(is_backup)
                local down_value = swap(down_value)
                ok,err = upstream.set_peer_down(upstream_name,is_backup,peer_id,down_value)
                if ok ~= nil then
                    ngx.say(ok)
                    ngx.log(ngx.DEBUG,"peer_id:",id)
                else
                    ngx.say(err)
                    ngx.log(ngx.DEBUG,"peer_id:",id)
                end
           }
        }

}
