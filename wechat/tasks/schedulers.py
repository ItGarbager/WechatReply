from apscheduler.schedulers.background import BackgroundScheduler

from wechat.tasks import call_back


def add_task(callback, hour, minute, *args, **kwargs):
    if hasattr(call_back, callback):
        scheduler.add_job(getattr(call_back, callback), 'cron', hour=hour, minute=minute, args=args, kwargs=kwargs)


scheduler = BackgroundScheduler()
