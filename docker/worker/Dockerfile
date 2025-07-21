FROM python:3.12

WORKDIR /worker

COPY ./worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./worker ./
COPY ./shared ./shared

ENV PYTHONPATH=/worker

CMD ["python", "main.py"]