from superset.daos.base import BaseDAO
from superset.extensions import db
from superset.models.external_token import ExternalToken


class ExternalTokenDAO(BaseDAO[ExternalToken]):
    @classmethod
    def get_by_id(cls, id: int | str) -> ExternalToken:
        externalToken = ExternalToken.get(id)

        return externalToken
