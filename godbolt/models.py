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
  "Library",
  "Compiler",
  "Language",
  "LanguageStream",
  "LibraryVersion"
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

    for k,v in self.kw.copy().items():
      if not v: self.kw.pop(k)
 
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
    asyncio.get_event_loop().create_task(self.__check_integrity())

  def __contains__(self, other: Union[str, LT, Any]) -> bool:
    for lang in self:
      if lang == other:
        return True

    return False

  async def __check_integrity(self) -> None:
    while True:
      for lang in self:
        if not isinstance(lang, Language): self.remove(lang)

      await asyncio.sleep(5)

  def append(self, item) -> None:
    if isinstance(item, Language): super().append(item)
    elif isinstance(item, dict): super().append(Language.from_dict(item))


class LibraryVersion(dict):
  __slots__ = ("version","alias","dependencies","path","libpath","options","staticliblink","id")

  description: str = None

  @classmethod
  def from_dict(cls, d):
    self = cls(id=d["id"],version=d["version"])
    for slot in cls.__slots__:setattr(self,slot,d[slot])
    if "description" in d: self.description = d["description"]
    return self

class Library:
  __slots__ = ("name","id","url",)

  versions: List[LibraryVersion] = []

  @classmethod
  def from_dict(cls, d):
    self=cls()
    for slot in cls.__slots__:setattr(self,slot,d.get(slot))
    for version in d["versions"]: self.versions.append(LibraryVersion.from_dict(version))
    return self

  def get_version(self, n):
    for version in self.versions:
      if version.id.lower()==n.lower(): return version

class Compiler(str):
  __slots__ = ("name","id","lang")
  alias: List[str] = []

  @classmethod
  def from_dict(cls, d):
    self=cls(d["name"])
    for slot in cls.__slots__:setattr(self,slot,d[slot])
    for alias in d["alias"]: self.alias.append(alias)
    self.lang = d["lang"]
    return self

class Language:
  def __init__(self, *, id: str, name: str, extensions: List[str], monaco: str, default_compiler: str) -> None:
    self.__id: str                 =           id
    self.__name: str               =          name
    self.__monaco: str             =        monaco
    self.__extensions: List[str]   =    extensions
    self.compilers: List[Compiler] = []
    self.libraries: List[Library]  = []
    self.default_compiler = default_compiler

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
      monaco=d["monaco"],
      default_compiler=d["defaultCompiler"]
    )

    return self

  def to_dict(self) -> dict:
    attrs: List[str] = ["extensions", "id", "name", "monaco","defaultCompiler"]
    ret: dict = {}
    for attr in attrs:
      ret[attr] = eval('self.{attr}'.format(attr=(attr if not attr.startswith("def") else "default_compiler")))

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

  def get_compiler(self, n):
    for compiler in self.compilers:
      if compiler.id.lower()==n.lower() or compiler.name.lower()==n.lower(): return compiler

  def get_library(self, n):
    for lib in self.libraries:
      if lib.name.lower()==n.lower() or lib.id.lower()==n.lower(): return lib

  def add_compiler(self, d):
    d["lang"] = self
    self.compilers.append(Compiler.from_dict(d))

class GodboltResponse:
  code: int
  did_execute: Optional[bool]
  build_result: Optional[dict]
  execution_time: Optional[str]
  stdout: List[dict]
  stderr: List[dict]
  asm_size: Optional[int]
  asm_result: Optional[List[dict]]
  slots = {
    "code": [],
    "didExecute": ["did_execute", True, bool], # name_in_attr, optional, type
    "buildResult": ["build_result", True],
    "execTime": ["execution_time", True, str],
    "stdout": [],
    "stderr": [],
    "asm_size": ["asmSize", True],
    "asm_result": ["asmResult", True]
  }

  @classmethod
  def from_dict(cls,d):
    self = cls()
    for n, slotv in self.slots.items():
      ren = n
      meth = lambda d: d
      if not slotv: setattr(self, ren, d[n]); continue
      if isinstance(slotv[0], str): ren = slotv[0]
      if callable(slotv[-1]): meth=slotv[-1]
      if len(slotv) in [1,2] and True in slotv: setattr(self, ren, meth(d.get(n))); continue

    return self
