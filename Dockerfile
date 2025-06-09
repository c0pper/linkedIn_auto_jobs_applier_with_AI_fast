FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create data directory
RUN mkdir -p /app/data_folder/output

CMD ["python", "main.py"]