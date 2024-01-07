import sched
import string
import sys
import uuid
from datetime import timedelta, datetime
from threading import Thread
from typing import Union, Optional

import sqlalchemy
from sqlalchemy import Engine, insert, LargeBinary, select, update, text
from sqlalchemy.orm import Session

from db.models import Page

DEFAULT_DURATION = timedelta(1)
DEFAULT_USES = 1000
CLEAR_PAGES_DELAY = 60
MAX_USES = 10_000
MAX_DURATION = timedelta(2)

SHORT_STR_ALPHABET = string.ascii_letters + string.digits + '-.'


def uuid2short_str(uid: uuid.UUID) -> str:
    number: int = uid.int
    s = ''
    for _ in range(24):
        s += SHORT_STR_ALPHABET[number % 64]
        number //= 64
    return s


def short_str2uuid(s: str) -> uuid.UUID:
    if len(s) != 24:
        raise ValueError('not an id')

    n = 0
    for char in reversed(s):
        n = n * 64 + SHORT_STR_ALPHABET.find(char)
    return uuid.UUID(int=n)


assert (short_str2uuid(uuid2short_str(uuid.UUID(int=1234))) == uuid.UUID(int=1234))


class DbStorage:
    def __init__(self, db: Engine):
        self.scheduler = sched.scheduler()
        self.db: Engine = db
        self.start_page_cleaner()

    def store(self, content: bytes, duration: timedelta, uses: int) -> str:
        if duration is None:
            duration = DEFAULT_DURATION
        if uses is None:
            uses = DEFAULT_USES

        with Session(self.db) as session:
            p = Page(content=content, expires=datetime.utcnow() + duration, uses=uses)
            session.add(p)
            session.flush()
            session.refresh(p)
            uid: uuid.UUID = p.id
            session.commit()
        return uuid2short_str(uid)

    def get(self, uid: str) -> str | None:
        uid = short_str2uuid(uid)
        with Session(self.db) as session:
            page = session.get(Page, uid)
            if page is None:
                return
            if page.expires <= datetime.utcnow() or page.uses < 1:
                session.delete(page)
                session.commit()
                return None

            page.uses -= 1
            session.commit()
            return page.content.decode("utf-8")

    def count(self) -> int:
        with Session(self.db) as session:
            return session.query(Page).count()

    def size(self) -> int:
        with Session(self.db) as session:
            return session.execute(text("select pg_database_size('postgres')")).scalar_one()

    def start_page_cleaner(self):
        thread = Thread(target=self.clear_pages)
        thread.start()

    def clear_pages(self):
        print('clearing pages')
        self.scheduler.enter(CLEAR_PAGES_DELAY, 1, self.clear_pages)

        with Session(self.db) as session:
            cnt = session.query(Page).where((Page.uses <= 0) | (Page.expires <= datetime.utcnow())).delete()
            print(f'pages cleared: {cnt}')
            session.commit()

        self.scheduler.run()

    def shutdown(self):
        print('stopping events!')
        list(map(self.scheduler.cancel, self.scheduler.queue))
