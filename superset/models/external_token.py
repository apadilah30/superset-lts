from __future__ import annotations

import logging

import sqlalchemy as sqla
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from flask_appbuilder.security.sqla.models import User
from markupsafe import escape, Markup
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped

from superset import app, db, is_feature_enabled, security_manager
from superset.models.helpers import AuditMixinNullable, ImportExportMixin

metadata = Model.metadata  # pylint: disable=no-member
config = app.config
logger = logging.getLogger(__name__)


class ExternalToken(Model, AuditMixinNullable, ImportExportMixin):
    """The external token object!"""

    __tablename__ = "external_tokens"
    id: Mapped[int] = Column(Integer, primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("ab_user.id"))
    # user: Mapped["User"] = relationship(back_populates="external_token")
    token = Column(Text)
    username = Column(String(255))
    consumed = Column(Integer)
    created_at = Column(DateTime)
    expired_at = Column(DateTime)
    consumed_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"Token(id={self.id!r}, name={self.username!r}, consumed_times={self.consumed!r})"
