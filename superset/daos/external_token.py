from typing import Optional, Union

from superset.daos.base import BaseDAO
from superset.extensions import db
from superset.models.external_token import ExternalToken


class ExternalTokenDAO(BaseDAO[ExternalToken]):
    @classmethod
    def get_by_id(cls, id: int | str) -> ExternalToken:
        externalToken = ExternalToken.get(id)

        return externalToken
    
    @staticmethod
    def validate_update_uniqueness(
        username: str, id: Optional[int] = None
    ) -> bool:
        """
        Validate if this username description is unique. `id` is optional
        and serves for validating on updates

        :param username: The username description
        :param id: This id is (only for validating on updates)
        :return: bool
        """
        query = db.session.query(ExternalToken).filter(
            ExternalToken.username == username, ExternalToken.id == id
        )
        if id:
            query = query.filter(ExternalToken.id != id)
        return not db.session.query(query.exists()).scalar()

