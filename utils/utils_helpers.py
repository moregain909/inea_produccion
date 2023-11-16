from decouple import config
import hashlib
import paramiko
import os
from dataclasses import dataclass, field
import shutil


@dataclass
class DataFile:
    name_ml: str = field(repr=True, default=None)
    name_data: str = field(repr=True, default=None)
    location_ml: str = field(repr=True, default=None)
    location_data: str = field(repr=True, default=None)
    hash: str = field(repr=True, default=None)
    timestamp_epoch: float = field(repr=False, default=None)
    timestamp_str: str = field(repr=True, default=None)

    def __post_init__(self):
        if self.name_ml:
            self.set_name_data()
            return True
        elif self.name_data:
            self.set_name_ml()
            return True
        else:
            print(f'La instancia {self} no tiene name_ml ni name_data')
            return False

    def set_name_ml(self):
        if self.name_data:
            self.name_ml = self.name_data
            return True
        else:
            print(f'Se requiere name_data para poder cargar name_ml de {self}')
            return False
    
    def set_name_data(self):
        if self.name_ml:
            self.name_data = self.name_ml.lower()
            return True
        else:
            print(f'Se requiere name para poder cargar name_data de {self}')
            return False

    def set_hash(self):

        pass

def hash_from_file(filename):
    """Genera un hash a partir del contenido del archivo.

    Args:
        filename (_str_): Nombre / path del archivo

    Returns:
        _str_: hash (Ej. "1c51ba5b4d9d3e189247a22db11e8f49e7056dbc")
    """
    hash_object = hashlib.sha1()
    with open(filename, "rb") as file:
        file_content = file.read()
        hash_object.update(file_content)

    return hash_object.hexdigest()

def ssh_send_file(file, host = "inea", port = "inea", username = "inea", password = "inea", \
                  local_dir = None, remote_dir = "/home/inea/sistemas/"):
    """Transfiere un archivo de la máquina local a un server ssh.

    Args:
        file (_type_): _description_
        host (str, optional): _description_. Defaults to "inea".
        port (str, optional): _description_. Defaults to "inea".
        username (str, optional): _description_. Defaults to "inea".
        password (str, optional): _description_. Defaults to "inea".
        remote_dir (str, optional): _description_. Defaults to "/home/inea/sistemas/".
    """

    hst = config("SERVER_INEA_LINUX_HOST") if host == "inea" else host
    psswrd = config("SERVER_INEA_LINUX_PASS") if password == "inea" else password
    prt = config("SERVER_INEA_LINUX_PORT") if port == "inea" else port

    if local_dir:
       os.chdir(local_dir)

    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hst, username = username, password = psswrd, port = prt)
    
    sftp = client.open_sftp()
    sftp.put(file, f"{remote_dir}{file}")
    
    sftp.close()
    client.close()

def copy_file(source_dir, destination_dir, source_filename, destination_filename):

    source_path = os.path.join(source_dir, source_filename)
    destination_path = os.path.join(destination_dir, destination_filename)

    try:
    # Copy the file from source to destination
    # shutil.copy2 preserve the original metadata as much as possible

        shutil.copy2(source_path, destination_path)
        print(f"File '{source_path}' copied to '{destination_path}'.")
        return True
    except FileNotFoundError:
        print(f"The file '{source_path}' does not exist.")
    except PermissionError:
        print(f"Permission error: Check if you have the necessary permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


if __name__ == "__main__":

    from utils_config import PATH2ML_REL, PATH2DATA_REL, FILES2CHECK
    
    path2root = os.path.join(os.path.dirname(__file__), "..")
    PATH2ML = os.path.join(path2root, PATH2ML_REL)
    PATH2DATA = os.path.join(path2root, PATH2DATA_REL)
    filename = "test_file.md"
    filename_data = "Test_FILE.md"
    print(copy_file(PATH2ML, PATH2DATA, filename, filename_data))
    pass