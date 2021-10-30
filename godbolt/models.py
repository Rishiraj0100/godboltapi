import requests

from typing import Any, Dict, List, Union
from urllib.parse import quote as uriquote


class Route:
  BASE: str = "https://godbolt.org/api"

  def __init__(self, method: str, path: str, **parameters: Any) -> None:
    self.path: str = path
    self.method: str = method.upper()
    url: str = self.BASE + self.path
    self.headers: Dict[str, str] = parameters.pop('headers', {}) or {}

    if parameters:
        url = url.format_map({k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
    self.url: str = url

  def request(self, *, json: bool = True) -> Union[Dict[str, Union[str, int]], requests.Response]:
    resp: requests.Response = requests.request(self.method, self.url, headers=self.headers)
    if json:
      return resp.json()

    return resp

class Language:
  def __init__(self, id: str, name: str, exts: List[str], monaco: str) -> None:
    self.__id: str                 =       id
    self.__name: str               =     name
    self.__extensions: List[str]   =     exts
    self.__monaco: str             =   monaco

  @property
  def id(self) -> str:
    return self.__id

  @property
  def name(self) -> str:
    return self.__name

  @property
  def monaco(self) -> str:
    return self.__monaco

  @property
  def extensions(self) -> List[str]:
    return self.__extensions


