FROM python:3.11-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY ./bot /app
RUN apk update
RUN apk add git
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 4001 4002 4003 4004 5000
CMD ["python", "-u", "main.py"]
