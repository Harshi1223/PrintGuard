import json

from subscriber import MQTTSubscriber
from processor import Processor
from anomaly_detector import AnomalyDetector
from dispatcher import Dispatcher
from health_calculator import HealthCalculator
from recommendation_engine import RecommendationEngine
from aggregator import Aggregator
from batch_manager import BatchManager
from config import BATCH_SIZE


processor = Processor()

detector = AnomalyDetector()

health = HealthCalculator()

recommendation = RecommendationEngine()

aggregator = Aggregator()

batch_manager = BatchManager(BATCH_SIZE)

dispatcher = Dispatcher()


def process_message(data):

    # -----------------------------
    # Validate Message
    # -----------------------------

    processed = processor.process(data)

    if processed is None:
        return

    # -----------------------------
    # Detect Faults
    # -----------------------------

    alerts = detector.detect(processed)

    # -----------------------------
    # Calculate Health
    # -----------------------------

    health_score, health_status = health.calculate(
        processed
    )

    # -----------------------------
    # Generate Recommendations
    # -----------------------------

    recommendations = recommendation.generate(
        alerts
    )

    # -----------------------------
    # Send through Dispatcher
    # -----------------------------

    output = dispatcher.dispatch(
        processed,
        alerts,
        recommendations,
        health_score,
        health_status
    )

    # -----------------------------
    # Aggregation
    # -----------------------------

    aggregator.update(output)

    summary = aggregator.get_summary()

    print("\n")

    print("=" * 80)

    print("FOG SUMMARY")

    print("=" * 80)

    print(
        json.dumps(
            summary,
            indent=4
        )
    )

    print("=" * 80)

    # -----------------------------
    # Batch Creation
    # -----------------------------

    batch = batch_manager.add_reading(output)

    if batch is not None:

        batch["summary"] = summary

        print("\n")

        print("=" * 80)

        print("FOG BATCH READY")

        print("=" * 80)

        print(
            json.dumps(
                batch,
                indent=4
            )
        )

        print("=" * 80)

        #
        # Next Phase:
        #
        # dispatcher.send_to_cloud(batch)
        #
        # This will send the batch to
        # AWS API Gateway.
        #


subscriber = MQTTSubscriber(process_message)

subscriber.start()