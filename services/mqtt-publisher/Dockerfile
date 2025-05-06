FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_publisher.py mqtt_publisher.py

CMD ["python", "mqtt_publisher.py"]
