FurrSight AI: PostgreSQL Database Schema
1. Database Engine
Engine: PostgreSQL

Reasoning: The project's goal is to create a structured dataset. PostgreSQL's relational model, data integrity constraints (foreign keys), and powerful SQL querying capabilities are essential for ensuring the quality and consistency of the data. Its native JSONB support provides flexibility where needed.

2. Table Schemas
Table: jobs

Purpose: Tracks the state and outcome of all asynchronous background tasks managed by Celery.

Columns:

id (UUID, Primary Key): Unique identifier for the job.

job_type (VARCHAR(50), Not Null): The type of job (e.g., 'SCRAPE_URL', 'PROCESS_IMAGE_PAIR', 'BATCH_INFERENCE').

status (VARCHAR(20), Not Null, Default: 'PENDING'): The current status of the job (e.g., 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED').

payload (JSONB): The input parameters for the job (e.g., URLs to scrape, model to use).

result (JSONB, Nullable): The output or result of a completed job.

error_message (TEXT, Nullable): Stores any error message if the job failed.

created_at (TIMESTAMPTZ, Not Null, Default: NOW()): Timestamp when the job was created.

started_at (TIMESTAMPTZ, Nullable): Timestamp when a worker started the job.

completed_at (TIMESTAMPTZ, Nullable): Timestamp when the job was completed or failed.

Table: dog_breeds

Purpose: A lookup table for canonical dog breed names.

Columns:

id (SERIAL, Primary Key): Unique identifier.

name (VARCHAR(100), Not Null, Unique): The name of the breed (e.g., 'Poodle', 'Golden Retriever').

Table: grooming_services

Purpose: A lookup table for grooming services or styles identified by the VLM.

Columns:

id (SERIAL, Primary Key): Unique identifier.

service_name (VARCHAR(100), Not Null, Unique): The name of the service (e.g., 'Lion Cut', 'Summer Shave', 'De-matting').

description (TEXT, Nullable): A brief description of the service.

Table: grooming_pairs

Purpose: The central table of the dataset, representing a single "before and after" transformation.

Columns:

id (UUID, Primary Key): Unique identifier for the pair.

before_image_url (TEXT, Not Null): S3/MinIO URL for the "before" image.

after_image_url (TEXT, Not Null): S3/MinIO URL for the "after" image.

source_url (TEXT, Nullable): Original URL where the images were found.

status (VARCHAR(20), Not Null, Default: 'UNVERIFIED'): Curation status (e.g., 'UNVERIFIED', 'VERIFIED', 'REJECTED').

dog_breed_id (INTEGER, Nullable, Foreign Key -> dog_breeds.id): The identified breed of the dog.

notes (TEXT, Nullable): Free-text notes from the research team.

created_at (TIMESTAMPTZ, Not Null, Default: NOW()): Timestamp of creation.

Table: pair_service_link

Purpose: A linking table to create a many-to-many relationship between grooming_pairs and grooming_services. A single grooming pair can involve multiple services.

Columns:

grooming_pair_id (UUID, Primary Key, Foreign Key -> grooming_pairs.id): The ID of the grooming pair.

grooming_service_id (INTEGER, Primary Key, Foreign Key -> grooming_services.id): The ID of the associated service.

