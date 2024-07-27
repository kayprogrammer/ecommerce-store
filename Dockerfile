FROM python:3.12-alpine

# Our Debian with Python and Nginx for python apps.
# See https://hub.docker.com/r/nginx/unit/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install bash and PostgreSQL client
RUN apk add --no-cache bash postgresql-client

COPY ./initial.sh /docker-entrypoint.d/initial.sh

RUN chmod +x /docker-entrypoint.d/initial.sh

RUN mkdir build

# We create folder named build for our app.
WORKDIR /build

COPY ./ ./
COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN chmod +x ./initial.sh

CMD ["bash", "./initial.sh"]

ENV PYTHONPATH=/build