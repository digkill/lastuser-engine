FROM python:3.12

WORKDIR /app

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./
COPY ./shared ./shared


ENV PYTHONPATH="${PYTHONPATH}:/shared"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
