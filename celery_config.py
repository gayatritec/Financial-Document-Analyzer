"""Celery configuration for financial document analyzer."""

import os
from celery import Celery
from conf import settings

# Create Celery app
celery_app = Celery(
    'financial_document_analyzer',
    broker=f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    backend=f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    include=['simple_celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure routing
celery_app.conf.task_routes = {
    'simple_celery_tasks.analyze_financial_document_task': {'queue': 'financial_analysis'},
    'simple_celery_tasks.process_investment_analysis_task': {'queue': 'investment_analysis'},
    'simple_celery_tasks.assess_risk_task': {'queue': 'risk_assessment'},
}

if __name__ == '__main__':
    celery_app.start()

