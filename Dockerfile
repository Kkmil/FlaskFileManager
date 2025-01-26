FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p uploads

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

EXPOSE 5000

#127.0.0.1
CMD ["flask", "run", "--host=0.0.0.0"] 
