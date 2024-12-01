FROM python:3.12.3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "todolist.wsgi:application"]
