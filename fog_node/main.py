from dotenv import load_dotenv
load_dotenv()

import json

from subscriber import MQTTSubscriber
from processor import Processor
from anomaly_detector import AnomalyDetector
from trend_detector import TrendDetector
from dispatcher import Dispatcher
from health_calculator import HealthCalculator
from recommendation_engine import RecommendationEngine
from aggregator import Aggregator
from batch_manager import BatchManager
from buffer import RetryBuffer
from config import BATCH_SIZE
import logger

log = logger.get_logger("main")

processor = Processor()

detector = AnomalyDetector()

# Novel addition: flags a sensor value trending upward across recent
# readings, BEFORE it crosses the hard threshold that AnomalyDetector
# checks - not present in standard threshold-based monitoring tools.
trend_detector = TrendDetector()

health = HealthCalculator()

recommendation = RecommendationEngine()

aggregator = Aggregator()

batch_manager = BatchManager(BATCH_SIZE)

dispatcher = Dispatcher()

# Retry buffer: if send_to_cloud() fails, the batch is saved here and
# retried automatically in the background every RETRY_INTERVAL seconds.
retry_buffer = RetryBuffer(dispatcher.send_to_cloud)
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
    # Halt Trigger (Critical only)
    # -----------------------------
    # Only Critical severity halts the printer - Medium/High-severity
    # alerts (Low Filament, High Humidity, Bed Overheat, High Vibration)
    # and Early Warning trend alerts stay as warnings only, since halting
    # on those either wastes a recoverable print or defeats the purpose
    # of an early warning. Critical (Nozzle Overheat) is the one condition
    # that is dangerous right now and worsens if ignored.

    if health_status == "Critical":
        critical_alerts = [a["type"] for a in alerts if a.get("severity") == "Critical"]
        subscriber.publish_command(
            processed["printer_id"],
            "HALT",
            reason=", ".join(critical_alerts) if critical_alerts else "Critical health status",
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