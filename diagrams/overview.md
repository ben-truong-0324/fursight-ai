FurrSight AI: System Architecture Specification
1. Project Goal & Philosophy
The primary objective is to build a robust, scalable platform for creating the FurrSight Grooming Dataset, a large-scale, structured collection of "before and after" dog grooming images. The system is designed as an internal research tool first, built with production-grade components to allow for a seamless future transition to a public-facing application. The architecture prioritizes a decoupled, microservices-based approach for maintainability and scalability.

2. Component Breakdown
The system is deployed as a set of containerized services within a single Kubernetes cluster, managed by a Traefik edge router.

2.1. Frontend Service

Technology: Next.js (React)

Role: Provides the primary User Interface (UI) for the research team.

Responsibilities:

Displaying and curating the grooming_pairs dataset.

Providing forms to initiate and monitor background jobs (e.g., web scraping, batch inference).

Communicating exclusively with the Backend API Service.

2.1.b Authentication Layer

Goal: To ensure only authorized research team members can access the platform and its data.

Method: The system will integrate with an Identity Provider (IdP) using standard protocols like OpenID Connect (OIDC) or SAML. All user-facing services (e.g., the web UI) and APIs will require authentication. This provides centralized user management and single sign-on (SSO) capabilities.

2.2. Backend API Service

Technology: FastAPI (Python)

Role: The central nervous system of the application; acts as a smart gateway.

Responsibilities:

Exposing a RESTful API for the Next.js frontend to consume.

Handling user authentication and authorization.

Validating incoming data.

Creating and dispatching jobs to the Redis Task Queue for background processing.

Querying the PostgreSQL database to serve data to the frontend.

Interacting with the Redis Cache to improve performance.

2.3. Inference Server

Technology: vLLM

Role: A dedicated, high-performance server for running ML models on GPUs.

Responsibilities:

Serves LLMs for tasks like generating creative search queries (Phase 1 of the project).

Serves Vision-Language Models (VLMs) for analyzing image pairs and identifying grooming services (Phase 3).

Accessed via internal cluster DNS by other services (e.g., FastAPI or Background Workers).

2.4. Cache & Task Queue

Technology: Redis

Role: A multi-purpose, in-memory data store.

Responsibilities:

Task Broker for Celery: Acts as the message queue for all asynchronous background jobs. This is its most critical function.

API Response Cache: Caches frequent database queries to reduce latency and load on PostgreSQL.

2.5. Background Workers

Technology: Celery & Python

Role: A fleet of stateless worker pods that execute long-running, asynchronous tasks.

Responsibilities:

Polling the Redis Task Queue for new jobs.

Executing specific Python scripts based on job type, such as:

scraper.py: Performs web scraping (Phase 2).

inference_job.py: Runs batch inference tasks using the vLLM server.

data_processor.py: Cleans and structures raw scraped data.

Interacts directly with Persistent Storage (PostgreSQL and S3).

2.6. Persistent Storage

PostgreSQL Database:

Role: The source of truth for all structured metadata.

Responsibilities: Stores information about jobs, verified grooming pairs, dog breeds, services, and relationships.

S3-Compatible Object Storage (MinIO):

Role: The store for all unstructured binary data.

Responsibilities: Stores raw scraped images, log files, dataset exports, and model artifacts.

3. Key Workflow: Asynchronous Web Scraping Job
A researcher uses the Next.js frontend to submit a form with scraping parameters.

The frontend sends a POST request to the FastAPI backend.

The FastAPI endpoint validates the request, creates a job message (e.g., { "task": "scrape", "params": {...} }), and pushes it to the Redis queue. It immediately returns a 202 Accepted response.

A Celery Worker pod, listening to the queue, picks up the job.

The Worker executes the scraper.py script with the job parameters.

The script downloads images to S3/MinIO and writes the associated metadata and job status updates to the PostgreSQL database.

The Next.js frontend periodically polls a FastAPI endpoint to get the job status from PostgreSQL and update the UI.
