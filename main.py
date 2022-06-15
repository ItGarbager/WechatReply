import threading

# from apscheduler.schedulers.background import BackgroundScheduler

from web import Application
from wechat.utils import wx


def main():
    app = Application()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(do, 'cron', hour='7-8', minute='1', args=['xxxxx@chatroom'])
    # objs = [wx, scheduler, app]

    objs = [wx, app]
    for obj in objs:
        _ = threading.Thread(target=obj.start, args=tuple())
        _.start()


if __name__ == '__main__':
    main()
