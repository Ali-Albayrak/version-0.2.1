# Use multi-stage builds
FROM python:3.10-slim as builder

WORKDIR /app

# Set environment variables
ENV POETRY_HOME=/opt/poetry     OETRY_VIRTUALENVS_IN_PROJECT=true     PATH="$POETRY_HOME/bin:$PATH"


# Copy only necessary files for installing dependencies
COPY . ./

# Install system dependencies
RUN apt update &&     apt --assume-yes install libpq-dev python3-dev gcc &&     pip3 install poetry

# Configure poetry and install Python dependencies
RUN poetry config virtualenvs.create true &&     poetry config virtualenvs.in-project true &&     poetry install --no-interaction --no-ansi -vvv --no-root


# Start a new stage for the final image
FROM python:3.10-slim

WORKDIR /app

# Copy environment variables
ENV PYTHONFAULTHANDLER=1     PYTHONHASHSEED=random     PYTHONUNBUFFERED=1     PORT=8080     WORKERS=2     UVICORN_LOG_LEVEL=error

# Copy app and vietualenv directories
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app /app


EXPOSE $PORT

CMD exec uvicorn api:app --host 0.0.0.0 --port $PORT --log-level $UVICORN_LOG_LEVEL --workers $WORKERS