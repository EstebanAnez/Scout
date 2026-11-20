import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# the tools read data files with paths relative to the repo root
os.chdir(ROOT)
