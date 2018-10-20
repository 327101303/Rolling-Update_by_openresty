    server {
        listen 8080;

        # sample output for the following /upstream interface:
        # upstream foo.com:
        #     addr = 127.0.0.1:80, weight = 4, fail_timeout = 53, max_fails = 100
        #     addr = 106.184.1.99:81, weight = 1, fail_timeout = 10, max_fails = 1
        # upstream bar:
        #     addr = 127.0.0.2:80, weight = 1, fail_timeout = 10, max_fails = 1
        location / {
            proxy_pass http://bar;
        }

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
                else
                    ngx.say(err)
                end
           }



        }

    }
