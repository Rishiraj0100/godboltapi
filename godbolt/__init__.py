import sys
import types
import aiohttp

from .models import *
from .cont import __version__, __author__
from aiohttp import ClientSession as Session
from typing import Any, Dict, List, Union, Mapping



class Godbolt:
  def __init__(self, headers: Dict[str, str] = {}, session: Session = None) -> None:
    headers = headers or {}
    py_version = ".".join([str(i) for i in tuple(sys.version_info)])
    if "final" in py_version: py_version=".".join(py_version.split(".")[:3])
    py_version=py_version.replace(".alpha.","a").replace(".beta.","b").replace(".candidate.","rc")

    headers['Accept'] = "application/json"
    headers['User-Agent'] = f"GodboltApi-Python-module/{__version__} (by Rishiraj0100;OpenSrc) Python/{py_version} aiohttp/{aiohttp.__version__} (A Python module for http requests; asynchronous)"

    self.__headers: Dict[str, str] = headers
    self.__languages: LanguageStream = LanguageStream()
    self.__session = session

  async def init(self,) -> None:
    languages = await Route(
      'GET',
      "/languages?fields={fields}",
      headers=self.__headers,
      fields="id,name,extensions,monaco,defaultCompiler"
    ).request(session=self.__session)

    if not self.__session: self.__session = Route.SESSION

    for language in languages:
      self.__languages.append(language)

    for language in self.languages:
      compilers = await Route(
        'get',
        '/compilers/{lang}?fields=id,name,lang,alias',
        headers=self.__headers,
        lang=language.id
      ).request()
      for compiler in compilers:
        language.add_compiler(compiler)

      libs = await Route(
        "Get",
        f"/libraries/{language.id}?fields=id,url,name,versions",
        headers=self.__headers
      ).request()
      for lib in libs: language.libraries.append(Library.from_dict(lib))

  @property
  def languages(self) -> LanguageStream:
    return self.__languages

  @property
  def headers(self) -> Mapping[str, str]:
    return types.MappingProxyType(self.__headers)

  def get_language(self, language: Union[str, Language, Any]) -> Union[None, Language]:
    for lang in self.languages:
      if lang == language:
        return lang

    return None

  async def execute(self, code: str, language=None, compiler=None, stdin = None, libraries: List[LibraryVersion]=[],):
    if not language and not compiler: compiler, language = self.get_language('python').default_compiler.id
    elif not compiler: compiler = self.get_language(language).default_compiler.id
    elif language and compiler:
      try: compiler = self.get_language(language).get_compiler(compiler).id
      except: raise ValueError(f"Compiler {compiler} for language {language} not found!")

    data = {
      "source": code,
      "compiler": compiler,
      "options": {
        "executeParameters": {},
        "compilerOptions": {
          "skipAsm": True
        },
        "filters": {
          "execute": True
        }
      }
    }

    if stdin: data["options"]["executeParameters"]["stdin"] = stdin
    if libraries: data["libraries"] = libraries

    resp = await Route('post',"/compiler/{compiler}/compile", compiler=compiler,json=data,headers=self.__headers).request()
    try: return {"output": "\n".join([i["text"] for i in resp["execResult"]["stdout"]]), "error": "\n".join([i["text"] for i in resp["execResult"]["stderr"]])}
    except: return resp   
