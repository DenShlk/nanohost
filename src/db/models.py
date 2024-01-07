import uuid
from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, LargeBinary, DateTime, UUID

# metadata = MetaData()
#
# pages = Table('pages', metadata,
#               Column('id', Integer, primary_key=True),
#               Column('content', LargeBinary),
#               Column('expires', DateTime)
#               )

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Page(Base):
    __tablename__ = "pages"
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    expires: Mapped[datetime]
    uses: Mapped[int]

    def __repr__(self) -> str:
        return f"Page(id={self.id!r}, expires={str(self.expires)}, uses={self.uses}, content={self.content[:100]!r})"
