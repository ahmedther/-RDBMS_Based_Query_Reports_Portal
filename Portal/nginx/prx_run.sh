#!/bin/sh

set -e

touch /etc/nginx/conf.d/default.conf 
touch /var/log/nginx/ehis_reports_portal.log
touch /var/log/nginx/ehis_reports_portal_log_error.log;
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'
