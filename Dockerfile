FROM python:3.6-alpine
RUN apk update && apk add alpine-sdk python3-dev libressl-dev linux-headers py3-cryptography libffi-dev make postgresql-dev
ADD . /code
WORKDIR /code
RUN pip3 install -r requirements.txt -r test_requirements.txt
CMD ["make", "test"]
