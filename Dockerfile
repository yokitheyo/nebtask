FROM python:3.11-slim

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/scripts

COPY scripts/start.sh /app/scripts/start.sh
RUN sed -i 's/\r$//' /app/scripts/start.sh && \
    chmod +x /app/scripts/start.sh

COPY . /app/

CMD ["/app/scripts/start.sh"]
