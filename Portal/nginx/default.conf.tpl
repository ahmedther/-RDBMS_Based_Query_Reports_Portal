

upstream app_server {
        server app:${SERVE_DJANGO_ON};
    }

server {
    listen ${LISTEN_PORT};

    client_max_body_size 100m;
    client_body_buffer_size 100m;
    
    access_log /var/log/nginx/ehis_reports_portal.log;
    error_log /var/log/nginx/ehis_reports_portal_log_error.log;

    client_body_timeout 86400s;
    client_header_timeout 86400s;
    keepalive_timeout 86400s;
    send_timeout 86400s;



    location /static {
        root /ehis_reports_portal;
    }

    location / {
        proxy_read_timeout 86400s;
        proxy_connect_timeout 86400s;
        proxy_send_timeout 86400s; 
        uwsgi_pass app_server;
        include /etc/nginx/uwsgi_params;

        # Set uWSGI timeout to one day (86400 seconds)
        uwsgi_read_timeout 8640;

    }

    location = /favicon.ico { access_log off; log_not_found off; }

   
}
