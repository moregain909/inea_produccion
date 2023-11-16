
import os, sys; 

path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#print(sys.path.append(os.path.dirname(os.path.realpath(__file__))))

from costos_envio.envio_helpers import *
from costos_envio.envio_config import *