import aiohttp
import asyncio

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
  "Language",
  "LanguageStream"
)

LT = TypeVar('LT', bound='Language')

class Route:
  BASE: str = "https://godbolt.org/api"
  SESSION: aiohttp.ClientSession = None

  def __init__(self, method: str, path: str, **parameters: Any) -> None:
    self.path: str = path
    self.method: str = method.upper()
    if method.lower()=="post" and ('json' in parameters or 'data' in parameters):
      self.kw: dict = {
        'json': parameters.pop('json', {}) or {},
        'data': parameters.pop('data', {}) or {}
      }
    else:
      self.kw: dict = {}

    if ('kw' in parameters or 'kwargs' in parameters):
      self.kw.update(parameters.pop('kw', {}) or {})
      self.kw.update(parameters.pop('kwargs', {}) or {})

    url: str = self.BASE + self.path
    self.headers: Dict[str, str] = parameters.pop('headers', {}) or {}

    if parameters:
        url = url.format_map({k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
    self.url: str = url

  async def request(self, *, session: aiohttp.ClientSession = None, json: bool = True) -> Union[dict, aiohttp.ClientResponse]:
    if not session:
      if not self.SESSION: self.__class__.SESSION = session = aiohttp.ClientSession()
      else: session = self.__class__.SESSION
    else: self.__class__.SESSION = session

    resp: aiohttp.ClientResponse = await session.request(self.method, self.url, headers=self.headers, **self.kw)
    if json:
      return await resp.json()

    return resp

class LanguageStream(list):
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.__dat = {}
    asyncio.get_event_loop().create_task(self.__check_integrity())

  def __contains__(self, other: Union[str, LT, Any]) -> bool:
    for lang in self:
      if lang == other:
        return True

    return False

  async def __check_integrity(self) -> None:
    while True:
      for lang in self:
        assert isinstance(lang, Language), "All attributes of this stream should be instance of Language not {lang.__class__!r}"
      await asyncio.sleep(5)

  def append(self, language: "Language"):
    self[language.name] = language
    super().append(language)

  def remove(self, language):
    if language in self:
      del self[language.name if isinstance(language, Language) else language]
    super().remove(language)

  __getitem__ = lambda self,attr: self.__dat[attr]
  def get(self, attr, default=None): return self.__dat.get(attr, default)
  def __setitem__(self, k,v): return self.__dat[k]=v
  def __delitem__(self,k): return self.__dat.__delitem__(k)


class Language:
  def __init__(self, *, id: str, name: str, extensions: List[str], monaco: str) -> None:
    self.__id: str                 =           id
    self.__name: str               =          name
    self.__monaco: str             =        monaco
    self.__extensions: List[str]   =    extensions
    self.compilers = []

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
      extensions=d["extensions"],
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
    resp = 'Language(id="{id}", name="{name}", extensions={exts}, monaco="{monaco}")'
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
