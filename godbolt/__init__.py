from typing import Dict


class Godbolt:
  def __init__(self, headers: Dict[str, str] = {}) -> None:
    headers['Accept'] = "application/json"
    self.__headers: Dict[str, str] = headers
