FROM python:3.10

RUN apt update

COPY source/main.py /main.py
COPY source/schema.py /schema.py
COPY source/message_translator.py /message_translator.py
COPY source/oop_parser.py /oop_parser.py
COPY source/exceptions.py /exceptions.py
COPY requirements.txt /requirements.txt
COPY .env /.env


RUN python -m pip install --upgrade pip && pip install -r ./requirements.txt

CMD ["python3", "main.py"]