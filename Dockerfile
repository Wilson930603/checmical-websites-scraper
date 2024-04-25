FROM selenium/standalone-chrome

USER root

RUN python3 --version
RUN apt-get update && apt-get install python3-distutils -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN apt-get install python3.8-dev -y
RUN apt-get install build-essential -y

WORKDIR /scripts/
COPY . /scripts
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ENV PYTHONPATH=/scripts
RUN ls
