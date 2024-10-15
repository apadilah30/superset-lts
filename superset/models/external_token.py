from __future__ import annotations

import uuid

from flask_appbuilder import Model
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped
from sqlalchemy_utils import UUIDType


class ExternalToken(Model):
    """The external token object!"""

    __tablename__ = "external_tokens"

    id: Mapped[int] = Column(Integer, primary_key=True)
    uuid = Column(UUIDType(binary=True), default=uuid.uuid4, primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("ab_user.id"))
    # user: Mapped["User"] = relationship(back_populates="external_token")
    token = Column(Text)
    username = Column(String(255))
    consumed = Column(Integer)
    created_on = Column(DateTime)
    expired_on = Column(DateTime)
    consumed_on = Column(DateTime)

    def __repr__(self) -> str:
        return f"Token(id={self.id!r}, name={self.username!r}, consumed_times={self.consumed!r})"
