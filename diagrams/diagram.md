

                                    INTERNAL RSX NETWORK (VPN/LAN)
                                                 │
                                                 │ Researcher Access
                                                 ▼
  +---------------------------------------------------------------------------------+
  |                            RESEARCH CLUSTER (e.g., k8s)                  |
  |                                                                                 |
  |   +-------------------------------------------------------------------------+   |
  |   |                             TRAEFIK (Edge Router)                       |   |
  |   |        (Handles internal hostnames: research.vpn.net, etc.)             |   |
  |   +---------------------------------┬----------------------┬----------------+   |
  |                                     │                      │                    |
  |   (For Interactive Tools)           │                      │ (For API Access)   |
  |                                     ▼                      ▼                    |
  |   +-------------------------+     +-----------------------------------------+   |
  |   |  Research Interface     |     |  Backend API Service                    |   |
  |   |  NextJS                |     |  (FastAPI Pod)                          |   |
  |   |                         |◄───►|  (Triggers jobs, serves metadata)       |   |
  |   +-------------------------+     +------------------┬------------------┬---+   |
  |                                                      │                  │       |
  |                      (Internal Cluster DNS Calls)    │ (Job Msg)        │ (Cache R/W)
  |                                                      ▼                  ▼       |
  |   +-------------------------+     +------------------+------------------+---+   |
  |   |  vLLM Inference Server  |     |  Cache & Task Queue (Redis Pod)         |   |
  |   |  (GPU Pods)             |     |                                     ◄───┤   |
  |   |                         |     |  (Celery uses this as a broker)         │   |
  |   +-------------------------+     +------------------▲------------------+---+   |
  |                                                      │ (Job Poll)       │       |
  |                                                      │                  │       |
  |   +--------------------------------------------------+------------------+---+   |
  |   |  Background Workers (Celery Worker Pods)                                |   |
  |   |                                                                     │   |   |
  |   |  ▶ Data Scrapers (scraper.py)                                       │   |   |
  |   |  ▶ Batch Inference (inference_job.py)                               │   |   |
  |   +--------------------------------------------------┬------------------+---+   |
  |                                                      │ (DB R/W)         │       |
  |                                                      ▼                  ▼       |
  |   +-------------------------------------------------------------------------+   |
  |   |                             PERSISTENT STORAGE                        |   |
  |   |                                                                         |   |
  |   |  ▶ PostgreSQL (Structured Metadata, Job Definitions & Results)        |   |
  |   |  ▶ S3 / MinIO (Raw Images, Datasets, Model Artifacts)                 |   |
  |   +-------------------------------------------------------------------------+   |
  |                                                                                 |
  +---------------------------------------------------------------------------------+