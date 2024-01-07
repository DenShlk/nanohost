import uuid
from datetime import datetime

from sqlalchemy import LargeBinary, UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


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
