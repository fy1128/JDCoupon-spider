FROM python:2.7-alpine
WORKDIR /usr/src/app
COPY . .

ENV TZ Asia/Shanghai

RUN set -ex; \
	\
	runDeps=' \
		libxml2 \
		libxslt \
		# follow issue to checkout mysql dependencies: https://github.com/gliderlabs/docker-alpine/issues/181
		#mariadb-client-libs \
		mariadb-connector-c-dev \
	'; \
	buildDeps='\
		libffi-dev \
		build-base \
		#openssl-dev \
		libressl-dev \
		libxslt-dev \
		libxml2-dev \
		mariadb-dev \
	'; \
	apk add --no-cache --virtual .run-deps $runDeps; \
	apk add --no-cache --virtual .build-deps \
		$buildDeps \
	; \
	# https://github.com/DefectDojo/django-DefectDojo/issues/407
	sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i.bkp; \
	pip install --no-cache-dir -r requirements.txt; \
	apk del .build-deps

COPY entrypoint.sh /usr/local/bin/
RUN chmod a+x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
#WORKDIR /usr/src/app/
#CMD [ "python", "main.py" ]

