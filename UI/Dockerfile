FROM python:3.6.5-alpine
WORKDIR /job-skill-app
ADD . /job-skill-app 
RUN pip install --upgrade pip
RUN pip install flask robobrowser flask-ngrok Werkzeug==0.16.1
CMD ["python", "index.py"]