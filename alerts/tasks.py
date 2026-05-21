from celery import shared_task
from .models import AlertRule
from .services import evaluate_all_alerts, evaluate_alert_rule


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_alerts_task(self):
    return evaluate_all_alerts()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_single_alert_task(self, alert_id):
    alert = AlertRule.objects.get(id=alert_id)
    return evaluate_alert_rule(alert)