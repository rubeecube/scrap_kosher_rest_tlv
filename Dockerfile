FROM alpine

RUN apk add --update --no-cache \
    python3 \
    py3-pip

COPY /app/. /app/
COPY /requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --break-system-packages --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/app

CMD ["python3", "scrap.py"]
