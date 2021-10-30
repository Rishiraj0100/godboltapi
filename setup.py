import random

from setuptools import setup

v = "0.0.1a"
ls = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

for i in range(5):
  v += ls[random.randint(0, len(ls)-1)] # randomized version per install

setup(
  name="GodBolt",
  packages=["godbolt"],
  version=v
)
