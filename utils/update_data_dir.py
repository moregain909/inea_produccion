#   ACTUALIZA ARCHIVOS EN DATA
#   Cuando se actualiza un archivo de data en el dir ML, 
#   actualiza el correspondiente archivo en el dir local DATA
#   y en el servidor INEA

#   Detecta si se actualiza algún archivo tanto en el dir ML como en el DATA
#   Si se actualiza algún archivo en el dir ML, se actualiza el mismo archivo en DATA y en SERVER INEA
#   Si se actualiza algún archivo en el dir DATA, se actualiza el mismo archivo en ML y en SERVER INEA

from os.path import exists
import os
import datetime
#import shutil
import time


from utils_helpers import hash_from_file, ssh_send_file, copy_file
from utils_helpers import DataFile
from utils_config import PATH2ML_REL, PATH2DATA_REL, FILES2CHECK

import sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

def main():

    """Chekea en ../INEA/ML si se actualizó alguno de los archivos 
    listados en FILES2CHECK y si hay cambios los actualiza en /DATA
    """
    
    filename = (__file__)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Configura paths absolutos a los directorios ML, DATA y del script actual
    PATH2ML = os.path.join(path2root, PATH2ML_REL)
    PATH2DATA = os.path.join(path2root, PATH2DATA_REL)
    SCRIPTPATH = os.path.realpath(os.path.dirname(__file__))
    
    os.chdir(SCRIPTPATH)


    ### for each file
    for f in FILES2CHECK:

    # opens file and generate hash
        actual_hash = hash_from_file(f)
        # print(f"actual hash {actual_hash}")

    # opens filename.txt containing last hash known
        txt_file_name = f.split(".")[-2] + ".txt"
        if not exists(txt_file_name):
            with open(txt_file_name, "x") as newtxt:
                print(f"Archivo {newtxt.name} creado")

        with open(txt_file_name, "r+") as txt_file:
            previous_hash = txt_file.read()
            # print(f"previous hash {previous_hash}")

            # compares file.txt file with actual hash

            if actual_hash != previous_hash:

                # updates file.txt with new hash
                txt_file.seek(0)
                txt_file.write(actual_hash)
                txt_file.truncate()

                # copy file and hashfile from ML to DATA
                copy_file(PATH2ML, PATH2DATA, f, f.lower())
                copy_file(PATH2ML, PATH2DATA, txt_file_name, txt_file_name.lower())

                # send file to production server
                #ssh_send_file(f, host = "inea", port = "inea", username = "inea", password = "inea", \
                #      local_dir = None, remote_dir = "/home/inea/sistemas/")

                # notify update
                print(f"--------- {timestamp}")
                print(f"script: {filename}")
                print()
                print(f"Archivo {f} actualizado\n")    

def old_main(FILES2CHECK):
    """Chekea si se actualizó alguno de los archivos listados en FILES2CHECK y si hay cambios los transfiere al server inea
    """
    
    filename = (__file__)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    
    path = os.path.realpath(os.path.dirname(__file__))
    os.chdir(path)
    # print(path)

    ### for each file
    for f in FILES2CHECK:

    # opens file and generate hash
        actual_hash = hash_from_file(f)
        # print(f"actual hash {actual_hash}")

    # opens filename.txt containing last hash known
        txt_file_name = f.split(".")[-2] + ".txt"
        if not exists(txt_file_name):
            with open(txt_file_name, "x") as newtxt:
                print(f"Archivo {newtxt.name} creado")

        with open(txt_file_name, "r+") as txt_file:
            previous_hash = txt_file.read()
            # print(f"previous hash {previous_hash}")

            # compares file.txt file with actual hash

            if actual_hash != previous_hash:

                # updates file.txt with new hash
                txt_file.seek(0)
                txt_file.write(actual_hash)
                txt_file.truncate()

                # send file to production server
                ssh_send_file(f, host = "inea", port = "inea", username = "inea", password = "inea", \
                      local_dir = None, remote_dir = "/home/inea/sistemas/")

                # notify update
                print(f"--------- {timestamp}")
                print(f"script: {filename}")
                print()
                print(f"Archivo {f} actualizado\n")
            # else:
            #     print(f"Archivo {f} no requiere actualización\n")


if __name__ == "__main__":
    
    main()

    pass