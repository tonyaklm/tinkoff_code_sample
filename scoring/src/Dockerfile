FROM python:3.10-slim

WORKDIR .
RUN pwd

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
RUN apt-get -y update; apt-get -y install curl

EXPOSE 8000

COPY src/ /

CMD ["python", "main.py"]