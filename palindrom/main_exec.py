import sys

def main_exec():
  # If a (patched) module is loaded, delete it
  if 'main' in sys.modules:  
    del sys.modules["main"]
  import main