FROM python:3.11-alpine
RUN apk update && apk add alpine-sdk python3-dev openssl-dev linux-headers py3-cryptography libffi-dev make postgresql-dev bash
ADD requirements.txt /usr/src/
ADD requirements-integration.txt /usr/src/
ADD requirements-unittest.txt /usr/src/
RUN pip3 install -r /usr/src/requirements-integration.txt
WORKDIR /code
CMD ["make", "integration-test"]
