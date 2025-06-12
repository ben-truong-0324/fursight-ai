# ---- Stage 1: Build ----
FROM python:3.12-slim as builder

# Set the working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to create the virtual environment in the project's root
RUN poetry config virtualenvs.in-project true

# Copy only the files needed to install dependencies
COPY apps/backend-fastapi/pyproject.toml apps/backend-fastapi/poetry.lock ./

# Install production dependencies
# --no-root: Don't install the project itself, just the dependencies
RUN poetry install --no-root


# ---- Stage 2: Final ----
# This stage copies the installed dependencies and our application code
# into a clean python image to create a small, optimized final image.
FROM python:3.12-slim as final

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy our application code
COPY apps/backend-fastapi/main.py .


# Activate the virtual environment by adding it to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]