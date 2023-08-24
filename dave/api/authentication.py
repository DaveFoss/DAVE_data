# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

from authlib.integrations.requests_client import OAuth2Session

from dave.settings import dave_settings


def auth_token(token, roles=False):
    """
    This functions verifies the user via jwt

    INPUT:

        **token** (dict) - jwt information from keycloak for authentification

    OPTIONAL:
        **role** (boolean, default False) - option to return also the roles for the user

    OUTPUT:
        **active_status** (boolean) - active status for the given jwt
        **roles** (boolean) - roles for the given jwt
    """
    # authentification
    oauth = OAuth2Session(
        client_id=dave_settings()["client_id"], client_secret=dave_settings()["client_secret_key"]
    )
    result = oauth.introspect_token(
        url=f"{dave_settings()['keycloak_server_url']}realms/dave/protocol/openid-connect/token/introspect",
        token=token["access_token"],
    )
    content = json.loads(result.content.decode())
    if roles:
        return content["active"], content["realm_access"]["roles"]
    else:
        return content["active"]
