#!/bin/sh

# Setup cron job
min=5
if [ -n "$INTERVAL" ]; then
	min=$INTERVAL
fi
(crontab -l ; echo "*/2 * * * * python /usr/src/app/main.py") | crontab -

# docker secret
if [ -n "$MYSQL_DB_PASS_FILE" ]; then
	echo "export MYSQL_DB_PASS=$(cat $MYSQL_DB_PASS_FILE)" >> ~/.profile
	export MYSQL_DB_PASS=$(cat $MYSQL_DB_PASS_FILE)
fi

exec crond -f -d 8
