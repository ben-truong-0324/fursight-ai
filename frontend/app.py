from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify,session
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import uuid
from authlib.integrations.flask_client import OAuth
import json
import time
import logging

app = Flask(__name__)
app.secret_key = 'temp_secret'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        content = file.read()
        # Send to Kafka (as base64 or bytes)
        message = {
            'id': photo_id,
            'filename': file.filename,
            'content': content.decode('latin1')  # OR use base64.b64encode(content).decode()
        }

        logger.info(f"[Kafka SEND] Topic: 'dog-photos' | Event: {message}")


        get_kafka_producer().send('dog-photos', message)
        session['photo_id'] = photo_id
        return redirect(url_for('assessment'))

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

    # In production: replace this with Redis or DB check
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

# KEYCLOAK_URL = "http://host.minikube.internal:8081"
# KEYCLOAK_REALM = "findex"
# DISCOVERY_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"
# KEYCLOAK_BROWSER_URL = "http://localhost:8081"
# CLIENT_ID = "flask-app"
# CLIENT_SECRET = "YOUR_KEYCLOAK_CLIENT_SECRET"

# oauth = OAuth(app)
# oauth.register(
#     name='keycloak',
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     # server_metadata_url='http://host.minikube.internal:8081/realms/findex/.well-known/openid-configuration',
#     server_metadata_url=DISCOVERY_URL,
#     client_kwargs={'scope': 'openid profile email'}
# )

