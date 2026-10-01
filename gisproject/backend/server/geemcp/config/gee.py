import json

import ee
from google.oauth2.credentials import Credentials

from server.geemcp.config.settings import setting


def initialize_gee() -> None:
    info = json.loads(setting.CREDENTIALS_PATH.read_text())
    credentials = Credentials(
        None,
        refresh_token=info["refresh_token"],
        token_uri=ee.oauth.TOKEN_URI,
        client_id=info.get("client_id", ee.oauth.CLIENT_ID),
        client_secret=info.get("client_secret", ee.oauth.CLIENT_SECRET),
        scopes=info.get("scopes", ee.oauth.SCOPES),
    )
    ee.Initialize(credentials, project=setting.GEE_PROJECT_ID)
