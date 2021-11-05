try:
  import ristpy
except ModuleNotFoundError:
  rist = "https://github.com/RistPy/PyRist/"
  raise RuntimeError(
    f'Module RistPy not found. Please install it as this API is written in rist {rist}'
  )

import os
import random

from setuptools import setup

for file in os.listdir('./godbolt/'):
  file = 'godbolt/'+file
  if file.endswith('.rist'):
    ristpy.rist(file, flags=ristpy.WRITE, compile_to=file[:-5]+'.py')

v = "0.0.1a"
if v.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            v += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            v += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass
setup(
  name="GodBolt",
  packages=["godbolt"],
  version=v
)
