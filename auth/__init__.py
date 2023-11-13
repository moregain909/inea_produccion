import os, sys; 

path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from auth.auth_helpers import *

#print(sys.path)