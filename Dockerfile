FROM ubuntu

RUN apt update -y && apt install -y python3-pip

WORKDIR /home/greenloop

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY python_scripts python_scripts
COPY resources resources

WORKDIR /home/greenloop/python_scripts

ENTRYPOINT [ "python3", "webserver.py" ]