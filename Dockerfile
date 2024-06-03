FROM python:3.9
COPY ./ ./
RUN apt-get update && apt-get install -y python3-pip
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]