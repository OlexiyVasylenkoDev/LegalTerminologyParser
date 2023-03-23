FROM python:3.10

RUN apt update

COPY main.py /main.py
COPY schema.py /schema.py
COPY message_translator.py /message_translator.py
COPY oop_parser.py /oop_parser.py
COPY exceptions.py /exceptions.py
COPY requirements.txt /requirements.txt
COPY .env /.env


RUN python -m pip install --upgrade pip && pip install -r ./requirements.txt

CMD ["python3", "main.py"]