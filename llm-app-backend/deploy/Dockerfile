FROM tiangolo/uwsgi-nginx-flask:python3.10-2022-11-11

COPY requirements.txt /app/requirements.txt
# Do not use pip-sync here as it removes uwsgi
RUN pip install --no-cache-dir --disable-pip-version-check --no-deps -r /app/requirements.txt
COPY / /app
COPY ./deploy/uwsgi.ini /app/uwsgi.ini
COPY ./deploy/nginx.conf /app/nginx.conf
RUN python manage.py collectstatic --noinput
