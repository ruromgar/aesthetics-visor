FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml

COPY app.py .
COPY visor ./visor

ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
