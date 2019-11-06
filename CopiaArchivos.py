import sys
import os
import hashlib
import _pickle as cPickle
import zipfile
from datetime import datetime
from pathlib import Path
import subprocess, time

timestampStr = datetime.now().strftime("%Y-%m-%d_%H-%M")
archivoActual = ""

def ejecuta(dir_path, origen, destino):
    """Ejecuta la copia: origen -> destino"""
    dict={}
    dir_origen = Path(origen)
    dir_destino = os.path.join(Path(dir_path), Path(destino))
    print(origen + '->' + dir_destino)
    zipZero = True
    os.chdir(dir_origen)

    try:
        chksm = os.path.join(dir_destino,"chksm.txt")
        if os.path.getsize(chksm) > 0:
            setArchivoActual(chksm)
            checksum = open(chksm,'rb')
            dict = cPickle.load(checksum)
            checksum.close()
    except IOError:
        num = sum([len(files) for r, d, files in os.walk(dir_origen)])
        cont = 0
        setArchivoActual(os.path.join(dir_destino,"chksm.txt"))
        checksum=open(os.path.join(dir_destino,"chksm.txt"),'wb')
        setArchivoActual(os.path.join(dir_destino,"ignore.txt"))
        ignore=open(os.path.join(dir_destino,"ignore.txt"),'w')

        for (path,dirs,files) in os.walk(dir_origen):
            if not os.path.exists(os.path.join(path,".caignore")):
                for archivo in files:
                    cont += 1
                    progreso(num,cont,os.path.join(path,archivo))
                    setArchivoActual(os.path.join(path,archivo))
                    f_temp = open(os.path.join(path,archivo),'rb')
                    content=f_temp.read()
                    m = hashlib.md5()
                    m.update(content)
                    dict[os.path.join(path,archivo)] = m.hexdigest()
                    f_temp.close()
            else:
                ignore.write(path)
                ignore.write('\n')

        if cont < num:
            progreso(num,num,'')

        cPickle.dump(dict,checksum)
        checksum.close()
        ignore.close()
        delta=zipfile.ZipFile(os.path.join(dir_destino,"delta.zip"),'w')
  
        cont = 0
        for (path,dirs,files) in os.walk(dir_origen):
            for archivo in files:
                cont += 1
                progreso(num,cont,os.path.join(path,archivo))
                zipZero = False
                setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                delta.write(os.path.join(path,archivo))
        delta.close()
  
        setArchivoActual(os.path.join(dir_destino,"remove.txt"))
        remove = open(os.path.join(dir_destino,"remove.txt"),'w')
        for k, v in list(dict.items()):
            if(not os.path.exists(k)):
                remove.write(k)
                remove.write('\n')
                del dict[k]
        remove.close()

        if zipZero:
            os.remove(os.path.join(dir_destino,"delta.zip"))
        else:
            renombraArchivo(dir_destino,timestampStr)
        return

    setArchivoActual(os.path.join(dir_destino,"remove.txt"))
    remove = open(os.path.join(dir_destino,"remove.txt"),'w')
    for k, v in list(dict.items()):
        if(not os.path.exists(k)):
            remove.write(k)
            remove.write('\n')
            del dict[k]
    remove.close()

    setArchivoActual(os.path.join(dir_destino,"ignore.txt"))
    ignore = open(os.path.join(dir_destino,"ignore.txt"),'w')
    delta = zipfile.ZipFile(os.path.join(dir_destino,"delta.zip"),'w')
    num = sum([len(files) for r, d, files in os.walk(dir_origen)])
    cont = 0
    for (path,dirs,files) in os.walk(dir_origen):
        if not os.path.exists(os.path.join(path,".caignore")):
            for archivo in files:
                cont += 1
                progreso(num,cont,os.path.join(path,archivo))
                setArchivoActual(os.path.join(path,archivo))
                f_temp = open(os.path.join(path,archivo),'rb')
                content = f_temp.read()
                m = hashlib.md5()
                m.update(content)
                f_temp.close()
                try:
                    if(dict[os.path.join(path,archivo)] != m.hexdigest()):
                        zipZero = False
                        setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                        delta.write(os.path.join(path,archivo))
                        dict[os.path.join(path,archivo)] = m.hexdigest()
                except KeyError:
                    zipZero = False
                    setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                    delta.write(os.path.join(path,archivo))
                    dict[os.path.join(path,archivo)] = m.hexdigest()
        else:
            ignore.write(path)
            ignore.write('\n')
    
    if cont < num:
        progreso(num,num,'')
    delta.close()
    ignore.close()

    setArchivoActual(os.path.join(dir_destino,"chksm.txt"))
    f=open(os.path.join(dir_destino,"chksm.txt"),'wb')
    cPickle.dump(dict,f)
    f.close()
    if zipZero:
        os.remove(os.path.join(dir_destino,"delta.zip"))
    else:
        renombraArchivo(dir_destino,timestampStr)


def renombraArchivo(dir_destino, timestampStr):
    """Renombra el archivo delta.zip al archivo de la fecha"""
    if os.path.exists(os.path.join(dir_destino,"delta.zip")):
        os.rename(os.path.join(dir_destino,"delta.zip"),os.path.join(dir_destino,timestampStr + ".zip"))


def directorioDestino(path):
    """Verifica la existencia y crea los directorios destino"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print("+ directorio " + path)
        except:
            print("")
            print(path + "--> Error destino: ", sys.exc_info())

def progreso(total, i, archivo):
    """Despliega el progreso de la ejecució"""
    incre = int(50.0 / total * i)
    espacios = 100 - len(archivo)
    if espacios < 0:
        espacios = 0
        archivo = archivo[:100]

    if i < total:
        sys.stdout.write('\r' + '| %d%%  |%s' % (2*incre,' '*5 + archivo + ' '*espacios))
    else:
        sys.stdout.write('\r' + '|%d%%  |%s' % (100,' '*5 + 'Finalizado' + ' '*90))
        sys.stdout.write('\n')
        print(total)
    sys.stdout.flush()

def setArchivoActual(nombre):
    """Registra el nombre del archivo en proceso"""
    global archivoActual
    archivoActual = nombre

def main():
    origen = ""
    destino = ""
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(os.path.join(dir_path,"detalle.txt")):
            raise Exception('No se encuentra el archivo detalle.txt')
    
        setArchivoActual(os.path.join(dir_path,"detalle.txt"))
        f_temp=open(os.path.join(dir_path,"detalle.txt"),'r')
        detalle = f_temp.readlines()
        for linea in detalle:
            if len(linea) == 0 or linea.startswith("#"):
                continue
        
            dirs = linea.replace('/','\\').rstrip().split(",")
            destino = os.path.join(Path(dir_path), Path(dirs[1]))
            origen = dirs[0]
            directorioDestino(os.path.join(Path(dir_path), Path(dirs[1])))

            if not os.path.isdir(dirs[0]):
                print("No existe el directorio origen: " + dirs[0])
            else:
                ejecuta(dir_path, dirs[0], dirs[1])

        f_temp.close()
        print("Finalizado")
    except:
        print("")
        print("Detalle del proceso ")
        print("   origen: " + origen)
        print("  destino: " + destino)
        print("  archivo: " + archivoActual)
        print("Info:", sys.exc_info())


if __name__ == "__main__":
    main()

