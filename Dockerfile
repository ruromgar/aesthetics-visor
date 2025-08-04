FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml

COPY . .
RUN uv pip install --system -e .

ENV DJANGO_SETTINGS_MODULE=visor_settings.settings
CMD ["uvicorn", "visor_settings.asgi:application", "--host", "0.0.0.0", "--port", "8501"]
