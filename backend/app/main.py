from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer, KafkaProducer
import threading
from app.kafka_worker import kafka_listener
app = FastAPI(title="Fursight API")

# Allow requests from Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://frontend-service"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Fursight backend is live"}

@app.post("/evaluate")
def evaluate():
    # Read image, do AI magic
    return {"result": "yes good"}

@app.on_event("startup")
def startup_event():
    print("🚀 Starting FastAPI + Kafka listener...")
    thread = threading.Thread(target=kafka_listener)
    thread.daemon = True
    thread.start()