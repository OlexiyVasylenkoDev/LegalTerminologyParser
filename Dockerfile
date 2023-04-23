FROM python:3.10

RUN apt update

COPY source /source
COPY requirements.txt /requirements.txt
COPY .env /.env


RUN python -m pip install --upgrade pip && pip install -r ./requirements.txt

CMD ["python3", "source/main.py"]