from dotenv import load_dotenv
load_dotenv()

import json

from subscriber import MQTTSubscriber
from processor import Processor
import anomaly_detector
import trend_detector as trend_detector_
import dispatcher as dispatcher_
import health_calculator
import recommendation_engine
import aggregator as aggregator_
import batch_manager as batch_manager_
import buffer
import config
import logger

log = logger.get_logger("main")

processor = Processor()

detector = anomaly_detector.AnomalyDetector()

# Novel addition: flags a sensor value trending upward across recent
# readings, BEFORE it crosses the hard threshold that AnomalyDetector
# checks - not present in standard threshold-based monitoring tools.
trend_detector = trend_detector_.TrendDetector()

health = health_calculator.HealthCalculator()

recommendation = recommendation_engine.RecommendationEngine()

aggregator = aggregator_.Aggregator()

batch_manager = batch_manager_.BatchManager(config.BATCH_SIZE)

dispatcher = dispatcher_.Dispatcher()

# Retry buffer: if send_to_cloud() fails, the batch is saved here and
# retried automatically in the background every RETRY_INTERVAL seconds.
retry_buffer = buffer.RetryBuffer(dispatcher.send_to_cloud)
retry_buffer.start_background_retry()


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
    # Detect Trends (early warning, before hard threshold is crossed)
    # -----------------------------

    trend_alerts = trend_detector.check(processed)

    alerts = alerts + trend_alerts

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

        # -----------------------------
        # Cloud Dispatch (with fallback)
        # -----------------------------

        success = dispatcher.send_to_cloud(batch)

        if success:
            log.info("Batch %s dispatched to cloud", batch["batch_id"])
        else:
            log.warning(
                "Batch %s could not be sent - saving to retry buffer",
                batch["batch_id"],
            )
            retry_buffer.save(batch)


subscriber = MQTTSubscriber(process_message)

subscriber.start()