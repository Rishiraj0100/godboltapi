import types

from .models import *
from aiohttp import ClientSession as Session
from typing import Any, Dict, List, Union, Mapping


class Godbolt:
  def __init__(self, headers: Dict[str, str] = {}, session: Session = None) -> None:
    headers = headers or {}
    headers['Accept'] = "application/json"
    self.__headers: Dict[str, str] = headers
    self.__languages: LanguageStream = LanguageStream()
    self.__session = session

  async def init(self,) -> None:
    languages = await Route('GET', "/languages", headers=self.__headers).request(self.__session)
    if not self.__session: self.__session = Route.SESSION
    for language in languages:
      self.__languages.append(Language.from_dict(language))
    for language in self.languages:
      compilers = Route(
        'get',
        '/compilers/{lang}',
        headers=self.__headers,
        lang=language.id
      ).request()
      for compiler in compilers:
        language.compilers.append(compiler)

  @property
  def languages(self) -> LanguageStream:
    return self.__languages.copy()

  @property
  def headers(self) -> Mapping[str, str]:
    return types.MappingProxyType(self.__headers)

  def get_language(self, language: Union[str, Language, Any]) -> Union[None, Language]:
    for lang in self.languages:
      if lang == language:
        return lang

    return None
