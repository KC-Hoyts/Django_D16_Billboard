import datetime
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

from board.models import Post


logger = logging.getLogger(__name__)


def my_job():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(date_creation__gte=last_week)

    readable_posts = "\n".join(["{} - {}".format(p.date_creation, p.title) for p in posts])
    readable_posts_html = "<br>".join(["{}-{}-{} {}:{} - {}".format(i.date_creation.day, i.date_creation.month, i.date_creation.year, i.date_creation.hour, i.date_creation.minute, i.title) for i in posts])

    users_email_list = set(User.objects.all().values_list('email', flat=True))

    subject = f'Посмотрите новые объявления за прошедшую неделю!'

    text_content = (
        f'Список новых объявлений: {readable_posts}...\n\n'
        f'Читать: http://127.0.0.1:8000/board/'
    )
    html_content = (
        f'<h3>Список новых объявлений за прошедшую неделю:</h3><br><br> '
        f'<i>{readable_posts_html}</i><br><br>'
        f'Загляните на <a href="http://127.0.0.1:8000/board/">сайт</a>, если что-то пропустили!')

    msg = EmailMultiAlternatives(subject, text_content, None, users_email_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", minute="15", hour="22"),
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
