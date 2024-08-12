FROM python:3.11-alpine
RUN apk update && apk add alpine-sdk python3-dev openssl-dev linux-headers py3-cryptography libffi-dev make postgresql-dev bash
ADD requirements.txt /usr/src/
ADD test_requirements.txt /usr/src
RUN pip3 install -r /usr/src/requirements.txt -r /usr/src/test_requirements.txt
WORKDIR /code
CMD ["make", "integration-test"]
