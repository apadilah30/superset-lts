from __future__ import annotations

import uuid

from flask_appbuilder import Model
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped
from sqlalchemy_utils import UUIDType
from superset.models.helpers import AuditMixinNullable


class ExternalToken(Model, AuditMixinNullable):
    """The external token object!"""

    __tablename__ = "external_tokens"

    id: Mapped[int] = Column(Integer, primary_key=True)
    uuid = Column(UUIDType(binary=True), default=uuid.uuid4, primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("ab_user.id"))
    # user: Mapped["User"] = relationship(back_populates="external_token")
    token = Column(Text)
    app = Column(String(255))
    tenant = Column(String(255))
    username = Column(String(255))
    consumed = Column(Integer)
    expired_on = Column(DateTime)
    consumed_on = Column(DateTime)
    

    def __repr__(self) -> str:
        return f"Token(id={self.id!r}, name={self.username!r}, consumed_times={self.consumed!r})"
