FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create data directory
RUN mkdir -p /app/data_folder/output

ENV PYTHONPATH=/app \
    DATA_FOLDER=/app/data_folder \
    PYTHONUNBUFFERED=1 \
    PORT=8054

# Expose both FastAPI and Gradio ports
EXPOSE 8054 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8054"]