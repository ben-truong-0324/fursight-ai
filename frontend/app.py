from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify,session
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import uuid
from authlib.integrations.flask_client import OAuth
import json
import time
import logging
import base64

app = Flask(__name__)
app.secret_key = 'temp_secret'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Silence Kafka debug noise
logging.getLogger("kafka").setLevel(logging.WARNING)
logging.getLogger("kafka.conn").setLevel(logging.WARNING)
logging.getLogger("kafka.client").setLevel(logging.WARNING)

producer = None

def get_kafka_producer():
    global producer
    if producer is not None:
        return producer

    for _ in range(10):
        try:
            producer_instance = KafkaProducer(
                bootstrap_servers='kafka.fursight.svc.cluster.local:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Connected to Kafka!")
            producer = producer_instance
            return producer
        except NoBrokersAvailable:
            print("⏳ Waiting for Kafka to become available...")
            time.sleep(5)
    raise Exception("❌ Failed to connect to Kafka after retries")


@app.route('/')
def index():
    user = session.get('user')
    token = session.get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['petPhoto']
    if file:
        photo_id = str(uuid.uuid4())
        content = base64.b64encode(file.read()).decode('utf-8')
        message = {
            'id': photo_id,
            'filename': file.filename,
            'content': content
        }
        logger.info(f"[Kafka SEND] Topic: 'dog-photos' | Event: {message}")
        get_kafka_producer().send('dog-photos', message).get(timeout=10)
        session['photo_id'] = photo_id
        return redirect(url_for('assessment'))
    elif not file:
        logger.warning("No file uploaded in request")
        return redirect(url_for('index'))

@app.route('/assessment')
def assessment():
    photo_id = session.get('photo_id')
    if not photo_id:
        logger.debug("No photo ID in session; redirecting to index.")
        return redirect(url_for('index'))

    logger.debug(f"Rendering assessment page for photo_id: {photo_id}")
    return render_template('assessment.html')


@app.route('/assessment/result')
def assessment_result():
    photo_id = session.get('photo_id')
    if not photo_id:
        logger.warning("No photo_id in session for /assessment/result")
        return jsonify({'status': 'error', 'message': 'no photo ID'}), 400

    # replace this with Redis or DB check
    consumer = KafkaConsumer(
        'dog-assessments',
        bootstrap_servers='kafka.fursight.svc.cluster.local:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=2000
    )

    for msg in consumer:
        logger.info(f"[Kafka RECEIVE] Topic: 'dog-assessments' | Message: {msg.value}")
        if isinstance(msg.value, dict) and msg.value.get('id') == photo_id:
            result = msg.value.get('result', 'No result')
            logger.info(f"[Kafka MATCH] photo_id: {photo_id} | Result: {result}")
            return jsonify({'status': 'ok', 'result': result})
    logger.debug(f"No Kafka match yet for photo_id: {photo_id}")
    return jsonify({'status': 'pending'})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

