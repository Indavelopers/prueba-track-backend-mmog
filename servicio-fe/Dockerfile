FROM python:3.14-slim

WORKDIR /webapp

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
