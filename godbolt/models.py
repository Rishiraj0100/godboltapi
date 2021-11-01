import requests

from typing import (
  Any,
  Dict,
  List,
  Union,
  TypeVar
)
from urllib.parse import quote as uriquote


__all__ = (
  "Route",
  "Language"
)

LT = TypeVar('LT', bound='Language')

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

  def request(self, *, json: bool = True) -> Union[dict, requests.Response]:
    resp: requests.Response = requests.request(self.method, self.url, headers=self.headers)
    if json:
      return resp.json()

    return resp

class Language:
  def __init__(self, *, id: str, name: str, exts: List[str], monaco: str) -> None:
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

  @classmethod
  def from_dict(cls, d: dict) -> LT:
    self = cls(
      id=d['id'],
      name=d["name"],
      exts=d["extensions"],
      monaco=d["monaco"]
    )

    return self

  def to_dict(self) -> dict:
    attrs: List[str] = ["extensions", "id", "name", "monaco"]
    ret: dict = {}
    for attr in attrs:
      ret[attr] = eval('self.{attr}'.format(attr=attr))

    return dict

  def __repr__(self) -> str:
    resp = 'Language(id="{id}", name="{name}", exts={exts}, monaco="{monaco}")'
    ret = resp.format(id=self.id, name=self.name, exts=self.extensions, monaco=self.monaco)
    return ret

  def __eq__(self, other: Union[LT, str, Any]) -> bool:
    if isinstance(other, Language):
      return other.id == self.id and other.name == self.name
    if isinstance(other, str):
      return self.id == other or self.name == other

    return False

  def __ne__(self, other: Union[LT, str, Any]) -> bool:
    return not self.__eq__(other)

  def __str__(self) -> bool:
    return self.name

