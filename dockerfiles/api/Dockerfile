FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
#COPY ../../plugins /app/plugins
#ENV PYTHONPATH="${PYTHONPATH}:/app/plugins"
RUN chmod -R 755 /app
