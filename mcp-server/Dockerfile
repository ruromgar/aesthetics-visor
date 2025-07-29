FROM python:3.12-slim
WORKDIR /srv

# 1️⃣ install uv once
RUN pip install --no-cache-dir uv

# 2️⃣ copy project metadata & lockfile first for better cache
COPY pyproject.toml uv.lock ./

# 3️⃣ install deps into system site-packages
RUN uv pip install --system -r pyproject.toml

# 4️⃣ copy rest of server code
COPY mcp-server .

# 5️⃣ expose port & launch
EXPOSE 3333
CMD ["uv", "run", "python", "-m", "mcp-server.server.py"]
