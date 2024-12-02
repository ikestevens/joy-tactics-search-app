# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY app.py .
COPY requirements.txt . 
COPY logo.png .
COPY ingest_data.py	 .
ADD dockerrun.sh . 
RUN chmod +x dockerrun.sh


# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*


RUN pip3 install -r requirements.txt

# CMD [ "python", "ingest_data.py"] 


EXPOSE 8501

CMD [ "./dockerrun.sh" ]

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
# ENTRYPOINT ["streamlit", "run", "app.py"]
# ENTRYPOINT ["streamlit", "run", "app.py"]
# ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=localhost"]