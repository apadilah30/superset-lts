from __future__ import annotations

import uuid

from flask_appbuilder import Model
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy_utils import UUIDType

from superset import security_manager
from superset.models.helpers import AuditMixinNullable


class ExternalToken(Model, AuditMixinNullable):
    """The external token object!"""

    __tablename__ = "external_tokens"


    id = Column(Integer, primary_key=True, autoincrement=True)
    # uuid = Column(UUIDType(binary=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(Integer, ForeignKey("ab_user.id"))
    user = relationship(
        security_manager.user_model, backref="external_tokens", foreign_keys=[user_id]
    )
    token = Column(Text)
    app = Column(String(255))
    tenant = Column(String(255))
    username = Column(String(255))
    consumed = Column(Integer)
    expired_on = Column(DateTime)
    consumed_on = Column(DateTime)
    

    def __repr__(self) -> str:
        return f"Token(id={self.id!r}, name={self.username!r}, consumed_times={self.consumed!r})"
