import hashlib
import os
import sys

BLOCKSIZE = 65536

def calculate_Hash(file_path):

    hasher = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

    with open(file_path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
    
        while len(buf) > 0:
            hasher.update(buf)
            sha1.update(buf)
            sha256.update(buf)
            sha512.update(buf)
        
            buf = afile.read(BLOCKSIZE)
        
    print("\nFile: {0}\n".format(file_path))
    print("MD5: {0}".format(hasher.hexdigest()))
    print("SHA1: {0}".format(sha1.hexdigest()))
    print("SHA256: {0}".format(sha256.hexdigest()))
    print("SHA512: {0}".format(sha512.hexdigest()))
    print("=" * 180 + "\n")


def main(file_name):
    dir_origen, arch_origen = os.path.split(file_name)
    search(dir_origen, arch_origen)


def search(dir_path, file_to_hash):
    for (path,dirs,files) in os.walk(dir_path):
        for filename in files:
            if (filename == file_to_hash):
                calculate_Hash(os.path.join(path,filename))
       

if __name__ == "__main__":
    file_name = ''
    for ar in sys.argv[1:]:
        file_name = file_name + ar + " "
    file_name = file_name.strip()
    if (len(file_name) == 0):
        print("Busca los archivos con el mismo nombre especificado, en todos los sub directorios y calcula su numeros Hash")
        print("el formato es -> python hashing.py <archivo>")
        sys.exit(2)
    main(file_name.strip())
