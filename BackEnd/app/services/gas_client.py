import json
from typing import Any, Dict, Optional

import requests


def post_to_gas(url: str, payload: Dict[str, Any]) -> Optional[requests.Response]:
    if not url:
        return None
    headers = {
        "Content-Type": "application/json",
    }
    return requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
