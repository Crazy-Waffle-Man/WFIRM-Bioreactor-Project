from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent.parent # Parent of parent of this file, should be ../
sys.path.insert(0, str(ROOT)) # Add files from root to path so that we can import from them

