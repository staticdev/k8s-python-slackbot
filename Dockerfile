FROM python:3.8.3-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# Set the working directory to /app
WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install "poetry==$POETRY_VERSION" \
  && poetry config virtualenvs.create false \
  && poetry install --no-dev

COPY src/* /app/

# Run app.py when the container launches
CMD ["python", "echobot.py"]
