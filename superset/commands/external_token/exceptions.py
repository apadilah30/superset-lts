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
from flask_babel import lazy_gettext as _

from superset.commands.exceptions import (
    CommandException,
    CommandInvalidError,
    CreateFailedError,
    DeleteFailedError,
    ValidationError,
)


class ExternalTokenInvalidError(CommandInvalidError):
    message = _("External Token parameters are invalid.")


class ExternalTokenCreateFailedError(CreateFailedError):
    message = _("External Token could not be created.")


class ExternalTokenUpdateFailedError(CreateFailedError):
    message = _("External Token could not be updated.")


class ExternalTokenNotFoundError(CommandException):
    message = _("External Token not found.")


class ExternalTokenDeleteFailedError(DeleteFailedError):
    message = _("External Tokens could not be deleted.")


class ExternalTokenDeleteIntegrityError(CommandException):
    message = _("External Token has associated annotations.")


class ExternalTokenNameUniquenessValidationError(ValidationError):
    """
    Marshmallow validation error for annotation layer name already exists
    """

    def __init__(self) -> None:
        super().__init__([_("Name must be unique")], field_name="name")
