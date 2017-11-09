FROM python:alpine3.6

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn -b 0.0.0.0:80 -w 4 --log-level DEBUG wsgi:app