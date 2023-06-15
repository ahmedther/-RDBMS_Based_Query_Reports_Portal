FROM python:3.11.3-slim as builder

LABEL maintainer='ahmed'

ENV PYTHONUNBUFFERED 1

WORKDIR /ehis_reports_portal

COPY ./requirements.txt ./

RUN apt update -y \
    && apt install  libpq-dev gcc libaio1  -y \ 
    && python3 -m venv /py \
    && /py/bin/pip install --upgrade pip \
    && /py/bin/pip install --no-cache --no-cache-dir -r ./requirements.txt  \
    && apt-get purge -y curl  unzip libpq-dev gcc libaio1 \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove -y  



FROM python:3.11.3-slim

LABEL maintainer='ahmed'

ENV PYTHONUNBUFFERED 1

COPY --from=builder /py /py

WORKDIR /ehis_reports_portal

COPY ./ ./



RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl unzip libaio1 cron \
    && mkdir -p /cx_oracle \
    && cd /cx_oracle \
    && curl -o instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip \
    && unzip -d . instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip \
    && rm -f instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip \
    && echo /cx_oracle/instantclient_21_9 > /etc/ld.so.conf.d/oracle-instantclient.conf  \
    && ldconfig \
    && ln -snf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && echo Asia/Kolkata > /etc/timezone \
    && mkdir /var/log/uwsgi \
    && touch /var/log/uwsgi/ehis_reports_portal.log \
    && apt-get purge -y curl  unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove -y  



ENV LD_LIBRARY_PATH=/cx_oracle/instantclient_21_9

ENV PATH="/py/bin:$PATH"

ENV PATH="/ehis_reports_portal/scripts:/py/bin:$PATH"

EXPOSE 8001

CMD ["./scripts/py_run.sh"]


# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000" ]CMD ["gunicorn", "--workers", "3", "--timeout", "86400", "--bind", "0.0.0.0:8004", "ehis_reports_portal.wsgi:application"]

