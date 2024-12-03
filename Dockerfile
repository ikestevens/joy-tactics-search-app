# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY app.py .
COPY requirements.txt . 
COPY logo.png .
COPY ingest_data.py	 .
ADD dockerrun.sh . 
RUN chmod +x dockerrun.sh

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py"]
