FROM ubuntu

RUN  apt-get -y update
RUN  apt-get -y install python3.6 python3.6-dev libssl-dev wget git python3-pip libmysqlclient-dev

WORKDIR /application

COPY . /application

RUN pip3 install -e .

EXPOSE 6543