# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

from authlib.integrations.requests_client import OAuth2Session
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2AuthorizationCodeBearer


def auth_token(token):
    """
    This functions verifies the user via jwt
    """
    # authentification
    oauth2_scheme = OAuth2AuthorizationCodeBearer(
        tokenUrl="http://127.0.0.1/auth/realms/dave/protocol/openid-connect/token",
        authorizationUrl="http://127.0.0.1/auth/realms/dave/protocol/openid-connect/auth",
    )
    # Get Token by user
    # token = keycloak_openid.token("test_dave", "test")['access_token']
    # token = request.headers['authorization'].replace("Bearer ", "")
    oauth = OAuth2Session(
        client_id="dave_login", client_secret="088d3f9e-58ea-405c-acf9-bf96b97ed922"
    )
    result = oauth.introspect_token(
        url="http://127.0.0.1/auth/realms/dave/protocol/openid-connect/token/introspect",
        token=token["access_token"],
    )
    content = json.loads(result.content.decode())
    if not content["active"]:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    else:
        return True
