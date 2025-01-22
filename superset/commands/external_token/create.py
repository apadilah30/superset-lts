# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging
from typing import Any

from flask_appbuilder.models.sqla import Model
from marshmallow import ValidationError

from superset.commands.external_token.exceptions import (
    ExternalTokenCreateFailedError,
    ExternalTokenInvalidError,
    ExternalTokenNameUniquenessValidationError,
)
from superset.commands.base import BaseCommand
from superset.daos.external_token import ExternalTokenDAO
from superset.daos.exceptions import DAOCreateFailedError

logger = logging.getLogger(__name__)


class CreateExternalTokenCommand(BaseCommand):
    def __init__(self, data: dict[str, Any]):
        self._properties = data.copy()

    def run(self) -> Model:
        self.validate()
        try:
            return ExternalTokenDAO.create(attributes=self._properties)
        except DAOCreateFailedError as ex:
            logger.info(f"error cuy: {ex.exception}")
            raise ExternalTokenCreateFailedError() from ex

    def validate(self) -> None:
        exceptions: list[ValidationError] = []

        username = self._properties.get("username", "")

        if not ExternalTokenDAO.validate_update_uniqueness(username):
            exceptions.append(ExternalTokenNameUniquenessValidationError())

        if exceptions:
            raise ExternalTokenInvalidError(exceptions=exceptions)
