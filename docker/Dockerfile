FROM python:3.6
WORKDIR /app

COPY ../dashboard ./dashboard
COPY ../location_list.json ./location_list.json
COPY ../requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app/dashboard

CMD ["python", "-m", "app.py"]
