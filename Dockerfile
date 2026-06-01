FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
ENV CRAWL4AI_URL=http://192.168.1.10:11235/md
ENV PROXY_API_KEY=
EXPOSE 8087
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8087"]
