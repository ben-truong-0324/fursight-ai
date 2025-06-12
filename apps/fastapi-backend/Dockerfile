# apps/fastapi/Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

# Copy only the dependency files to leverage Docker layer caching
COPY poetry.lock pyproject.toml ./

# Install dependencies using the lock file for reproducible builds
RUN poetry install --no-dev --no-root

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8009

# Command to run the application using uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]