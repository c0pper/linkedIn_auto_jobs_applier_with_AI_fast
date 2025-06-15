FROM python:3.10-slim as base

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


# API Service
FROM base as api
COPY . .
RUN mkdir -p /app/data_folder/output
ENV PYTHONPATH=/app \
    DATA_FOLDER=/app/data_folder \
    PYTHONUNBUFFERED=1 \
    PORT=8054
EXPOSE 8054
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8054"]


# Gradio UI Service
FROM base as gradio-ui
COPY src/interfaces/gradio_ui.py .
COPY src/api/ ./api/
COPY src/models/ ./models/
ENV PYTHONPATH=/app \
    API_URL=http://api:8054/api
EXPOSE 7860
CMD ["python", "gradio_ui.py"]

# COPY . .

# # Create data directory
# RUN mkdir -p /app/data_folder/output

# ENV PYTHONPATH=/app \
#     DATA_FOLDER=/app/data_folder \
#     PYTHONUNBUFFERED=1 \
#     PORT=8054

# # Expose both FastAPI and Gradio ports
# EXPOSE 8054 7860

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8054"]