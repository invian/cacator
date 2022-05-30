FROM python:3.8.13-buster

WORKDIR /app

RUN pip3 install --upgrade pip && pip3 install pipenv

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pipenv install --deploy --clear --system;

COPY dashboard/public ./dashboard/public
COPY shared/ /app/shared/
COPY server/ /app/server/

EXPOSE 53/udp
EXPOSE 5053
ENTRYPOINT ["python3", "-m", "server.api"]
