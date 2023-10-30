import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta

from ... models import *

logger = logging.getLogger(__name__)


def my_job():
    template = 'pages/mail_weekly_posts.html'
    start_date = datetime.today() - timedelta(days=6)
    this_weeks_posts = Post.objects.filter(date__gt=start_date)
    for cat in Category.objects.all():
        post_list = this_weeks_posts.filter(category__name=cat)
        if post_list:
            subscribers = cat.subscribers.all()
            context = {
                'post_list': post_list,
                'cat': cat,
            }

            for sub in subscribers:
                context['sub'] = sub
                html_content = render_to_string(template, context)

                msg = EmailMultiAlternatives(
                    subject=f'{cat.name}: Посты за прошедшую неделю',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[sub.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                # print(html_content)


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day="7"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="10", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")