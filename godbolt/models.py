import requests

from typing import Any, Dict, Union
from urllib.parse import quote as uriquote


class Route:
  BASE: str = "https://godbolt.org/api"

  def __init__(self, method: str, path: str, **parameters: Any) -> None:
    self.path: str = path
    self.method: str = method.upper()
    url = self.BASE + self.path
    self.headers = parameters.pop('headers', {}) or {}

    if parameters:
        url = url.format_map({k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
    self.url: str = url

  def request(self, *, json: bool = True) -> Union[Dict[str, Union[str, int]], requests.Response]:
    resp: requests.Response = requests.request(self.method, self.url, headers=self.headers)
    if json:
      return resp.json()

    return resp
