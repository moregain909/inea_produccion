from typing import Union, Dict, Type


import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

# Paths relativos (desde el ROOT) a ML y data
PATH2ML_REL = "../INEA/ML"
PATH2DATA_REL = "data"

# Archivos a monitorear y actualizar
FILES2CHECK = ["test_file.md", "Publis_GBP.xlsx", "Costos_01_GBP.xls", "Articulos_GBP_extendida.xlsx", "Articulos_GBP.xlsx"]

