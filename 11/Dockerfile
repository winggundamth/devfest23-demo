FROM python:3.12.1-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py utils.py ./

EXPOSE 8000

CMD python main.py
