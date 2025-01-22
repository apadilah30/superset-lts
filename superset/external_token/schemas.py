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


from marshmallow import fields, Schema
from marshmallow.validate import Length

from superset.dashboards.schemas import UserSchema

id_description = "Unique if of external token filter"
username_description = "Name of external token filter"
token_description = "Token of external token"
app_description = "App Name of external token"
tenant_description = "Tenant Name of external token"

get_delete_ids_schema = {"type": "array", "items": {"type": "integer"}}

openapi_spec_methods_override = {
    "get": {"get": {"summary": "Get an ExternalToken"}},
    "get_list": {
        "get": {
            "summary": "Get a list of ExternalToken",
            "description": "Gets a list of ExternalToken, use Rison or JSON "
                           "query parameters for filtering, sorting,"
                           " pagination and for selecting specific"
                           " columns and metadata.",
        }
    },
    "delete": {"delete": {"summary": "Delete an ExternalToken"}},
    "info": {"get": {"summary": "Get metadata information about this API resource"}},
}


class TablesSchema(Schema):
    schema = fields.String()
    table_name = fields.String()
    id = fields.Integer()


class ExternalTokenListSchema(Schema):
    id = fields.Integer(metadata={"description": "id_description"})
    username = fields.String(metadata={"description": "username_description"})
    token = fields.String(metadata={"description": "token_description"})
    app = fields.String(metadata={"description": "app_description"})
    tenant = fields.String(metadata={"description": "tenant_description"})
    user = fields.Nested(UserSchema)


class ExternalTokenShowSchema(Schema):
    id = fields.Integer(metadata={"description": "id_description"})
    username = fields.String(metadata={"description": "username_description"})
    token = fields.String(metadata={"description": "token_description"})
    app = fields.String(metadata={"description": "app_description"})
    tenant = fields.String(metadata={"description": "tenant_description"})
    user = fields.Nested(UserSchema)


class ExternalTokenPostSchema(Schema):
    username = fields.String(
        metadata={"description": "username_description"},
        required=True,
        allow_none=False,
        validate=Length(1, 255),
    )
    token = fields.String(
        metadata={"description": "token_description"},
        required=True,
        allow_none=False,
        validate=Length(1, 255)
    )
    app = fields.String(
        metadata={"description": "app_description"},
        required=True,
        allow_none=False,
        validate=Length(1, 255)
    )
    tenant = fields.String(
        metadata={"description": "tenant_description"},
        required=True,
        allow_none=False,
        validate=Length(1, 255)
    )
    user_id = fields.Integer(
        metadata={"description": "user_id_description"},
        required=True,
        allow_none=False,
    )


class ExternalTokenPutSchema(Schema):
    username = fields.String(
        metadata={"description": "username_description"},
        required=False,
        allow_none=False,
        validate=Length(1, 255),
    )
    token = fields.String(
        metadata={"description": "token_description"},
        required=False,
        allow_none=False,
        validate=Length(1, 255)
    )
    app = fields.String(
        metadata={"description": "app_description"},
        required=False,
        allow_none=False,
        validate=Length(1, 255)
    )
    tenant = fields.String(
        metadata={"description": "tenant_description"},
        required=False,
        allow_none=False,
        validate=Length(1, 255)
    )
    user_id = fields.Integer(
        metadata={"description": "user_id_description"},
        required=True,
        allow_none=False,
    )
