FROM python:3.6
WORKDIR /app

ADD .. covid_dashboard
WORKDIR /app/covid_dashboard

RUN pip install -r requirements.txt

WORKDIR /app/covid_dashboard/dashboard

CMD ["python", "app.py"]
