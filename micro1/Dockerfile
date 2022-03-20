FROM python:3.8-alpine3.10
LABEL maintainer="dmozh58@gmail.com"

COPY . ./
RUN apk add bind-tools

#RUN apt-get -y upgrade && apt-get -y update
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

CMD ["python3", "__main__.py"]