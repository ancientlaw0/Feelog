#!/bin/bash

# copy .env if needed
if [ ! -f .env ]; then
    echo ".env not found, copying from .env.example..."
    cp .env.example .env
fi

#waiting for Elasticsearch to become reachable
echo "Waiting for Elasticsearch to be available at $ELASTICSEARCH_URL..."
until curl -s $ELASTICSEARCH_URL > /dev/null; do
    echo " Elasticsearch not reachable. Retrying in 2s..."
    sleep 2
done
echo "Elasticsearch is UP at $ELASTICSEARCH_URL"

# Run seed-admin (migrations + admin setup)
echo "Running seed-admin (includes migrations)..."
flask seed-admin


echo " Starting Feelog..."
exec gunicorn -b :5000 "wsgi:app"
