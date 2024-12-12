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

from flask import request, Response
from flask_appbuilder.api import expose, permission_name, protect, rison, safe
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import ngettext
from marshmallow import ValidationError

from superset.external_token.filters import ExternalTokenAllTextFilter
from superset.external_token.schemas import (
    ExternalTokenListSchema,
    ExternalTokenShowSchema,
    ExternalTokenPostSchema,
    ExternalTokenPutSchema,
    get_delete_ids_schema,
    openapi_spec_methods_override,
)
from superset.commands.external_token.create import CreateExternalTokenCommand
from superset.commands.external_token.delete import DeleteExternalTokenCommand
from superset.commands.external_token.exceptions import (
    ExternalTokenCreateFailedError,
    ExternalTokenDeleteFailedError,
    ExternalTokenDeleteIntegrityError,
    ExternalTokenInvalidError,
    ExternalTokenNotFoundError,
    ExternalTokenUpdateFailedError,
)
from superset.commands.external_token.update import UpdateExternalTokenCommand
from superset.constants import MODEL_API_RW_METHOD_PERMISSION_MAP, RouteMethod
from superset.extensions import event_logger
from superset.models.external_token import ExternalToken
from superset.views.base_api import (
    BaseSupersetModelRestApi,
    requires_json,
    statsd_metrics,
)

logger = logging.getLogger(__name__)


class ExternalTokenRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(ExternalToken)

    include_route_methods = RouteMethod.REST_MODEL_VIEW_CRUD_SET | {
        RouteMethod.RELATED,
        "bulk_delete",  # not using RouteMethod since locally defined
    }
    class_permission_name = "External Token"
    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP

    resource_name = "external_token"
    allow_browser_login = True

    show_columns = [
        "id",
        "username",
        "token",
        "app",
        "tenant",
    ]
    list_columns = [
        "id",
        "username",
        "token",
        "app",
        "tenant",
        # "created_by.first_name",
        # "created_by.last_name",
        # "changed_by.first_name",
        # "changed_by.last_name",
        "changed_on",
        "changed_on_delta_humanized",
        # "created_on",
    ]
    add_columns = ["username", "token"]
    edit_columns = add_columns
    add_model_schema = ExternalTokenPostSchema()
    list_model_schema = ExternalTokenListSchema()
    show_model_schema = ExternalTokenShowSchema()
    edit_model_schema = ExternalTokenPutSchema()

    order_columns = [
        "username",
        "token",
        # "created_by.first_name",
        # "changed_by.first_name",
        "changed_on",
        "changed_on_delta_humanized",
        # "created_on",
    ]

    search_filters = {"username": [ExternalTokenAllTextFilter]}
    # allowed_rel_fields = {"created_by", "changed_by"}

    apispec_parameter_schemas = {
        "get_delete_ids_schema": get_delete_ids_schema,
    }
    openapi_spec_tag = "External Token"
    
    openapi_spec_methods = openapi_spec_methods_override
    """ Overrides GET methods OpenApi descriptions """

    @expose("/<int:pk>", methods=("DELETE",))
    @protect()
    @safe
    @statsd_metrics
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.delete",
        log_to_statsd=False,
    )
    @permission_name("delete")
    def delete(self, pk: int) -> Response:
        """Delete an external token.
        ---
        delete:
          summary: Delete an external token
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
            description: The external token pk for this annotation
          responses:
            200:
              description: Item deleted
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            DeleteExternalTokenCommand([pk]).run()
            return self.response(200, message="OK")
        except ExternalTokenNotFoundError:
            return self.response_404()
        except ExternalTokenDeleteIntegrityError as ex:
            return self.response_422(message=str(ex))
        except ExternalTokenDeleteFailedError as ex:
            logger.error(
                "Error deleting external token %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/", methods=("POST",))
    @protect()
    @safe
    @statsd_metrics
    @permission_name("post")
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.post",
        log_to_statsd=False,
    )
    @requires_json
    def post(self) -> Response:
        """Create a new external token.
        ---
        post:
          summary: Create a new external token
          requestBody:
            description: External Token schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
          responses:
            201:
              description: External Token added
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: number
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.add_model_schema.load(request.json)
        # This validates custom Schema with custom validations
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            new_model = CreateExternalTokenCommand(item).run()
            return self.response(201, id=new_model.id, result=item)
        except ExternalTokenNotFoundError as ex:
            return self.response_400(message=str(ex))
        except ExternalTokenInvalidError as ex:
            return self.response_422(message=ex.normalized_messages())
        except ExternalTokenCreateFailedError as ex:
            logger.error(
                "Error creating annotation %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/<int:pk>", methods=("PUT",))
    @protect()
    @safe
    @statsd_metrics
    @permission_name("put")
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.put",
        log_to_statsd=False,
    )
    @requires_json
    def put(self, pk: int) -> Response:
        """Update an external token.
        ---
        put:
          summary: Update an external token
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
            description: The external token pk for this annotation
          requestBody:
            description: External Token schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
          responses:
            200:
              description: External Token changed
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: number
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.edit_model_schema.load(request.json)
            item["layer"] = pk
        # This validates custom Schema with custom validations
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            new_model = UpdateExternalTokenCommand(pk, item).run()
            return self.response(200, id=new_model.id, result=item)
        except ExternalTokenNotFoundError:
            return self.response_404()
        except ExternalTokenInvalidError as ex:
            return self.response_422(message=ex.normalized_messages())
        except ExternalTokenUpdateFailedError as ex:
            logger.error(
                "Error updating annotation %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/", methods=("DELETE",))
    @protect()
    @safe
    @statsd_metrics
    @rison(get_delete_ids_schema)
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.bulk_delete",
        log_to_statsd=False,
    )
    def bulk_delete(self, **kwargs: Any) -> Response:
        """Bulk delete external tokens.
        ---
        delete:
          summary: Delete multiple external tokens in a bulk operation
          parameters:
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/get_delete_ids_schema'
          responses:
            200:
              description: CSS templates bulk delete
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        item_ids = kwargs["rison"]
        try:
            DeleteExternalTokenCommand(item_ids).run()
            return self.response(
                200,
                message=ngettext(
                    "Deleted %(num)d external token",
                    "Deleted %(num)d external tokens",
                    num=len(item_ids),
                ),
            )
        except ExternalTokenNotFoundError:
            return self.response_404()
        except ExternalTokenDeleteIntegrityError as ex:
            return self.response_422(message=str(ex))
        except ExternalTokenDeleteFailedError as ex:
            return self.response_422(message=str(ex))
