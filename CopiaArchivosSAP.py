import os
import hashlib
import pickle as cPickle
from datetime import datetime, timedelta
from pathlib import Path
from msvcrt import getch
import shutil
import time
import filecmp
import ClassProgressBar


dirBackup = "D:\\oracle\P01\\sapbackup"
p = ClassProgressBar.ProgressBar('Copiando backup...')

def countFiles(directory):
    """ Cantidad de archivos """
    files = []
    if os.path.isdir(directory):
        for path, dirs, filenames in os.walk(directory):
            files.extend(filenames)
    return len(files)

def makedirs(dest):
    """ Crea directorios faltantes """
    if not os.path.exists(dest):
        os.makedirs(dest)

def copyFilesWithProgress(src, dest):
    """ Copia de archivos con indicador de progreso """
    numFiles = countFiles(src)
    if numFiles > 0:
        makedirs(dest)
    
    numCopied = 0
    
    for path, dirs, filenames in os.walk(src):
        for directory in dirs:
            destDir = path.replace(src, dest)
            makedirs(os.path.join(destDir, directory))
            
        for sfile in filenames:
            srcFile = os.path.join(path, sfile)
            destFile = os.path.join(path.replace(src, dest), sfile)
            shutil.copy(srcFile, destFile)
            numCopied += 1
            p.calculateAndUpdate(numCopied, numFiles)
            print

def copiarBK():
    """ Ejecuta la sincronizacion de backup """

    print("[+] Sincronizando " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    writeLog("Inicio sinc. backup")

    # Backup
    origen = "V:\\BackupEpsas"
    destino = "D:\\oracle\\P01\\sapbackup\\BackupEpsas"
    ignorar = ["P01", "log", "temp"]
    cont = 0
    copiados = 0
    writeLog("Backup " + origen + " -> " + destino)
    for (root,dirs,files) in os.walk(origen, topdown=True):
        dirs.sort(reverse=True)
        for dir in dirs:
            cont += 1
            if not dir in ignorar:
                try:
                    dirPath = os.path.join(root, dir)
                    ctimeOrigen = os.stat(dirPath).st_ctime
                    dirDestino = os.path.join(destino,dir)
                    
                    ctimeDestino = 0
                    resultCmp = False
                    if os.path.isdir(dirDestino):
                        ctimeDestino = os.stat(dirDestino).st_ctime
                        resultCmp = filecmp.dircmp(dirPath,dirDestino)
                    if not resultCmp and datetime.now() <= datetime.fromtimestamp(ctimeOrigen) + timedelta(days=10):
                        writeLog("Directorios no son iguales o no existe " + dirPath + " ->" + dirDestino)
                        copiados += 1
                        if ctimeDestino != 0:
                            writeLog("Copiando " + dirPath + "(" + datetime.fromtimestamp(ctimeOrigen).strftime("%Y-%m-%d %H:%M:%S") + ") ->" + dirDestino + "(" + datetime.fromtimestamp(ctimeDestino).strftime("%Y-%m-%d %H:%M:%S") + ")")
                        else:
                            writeLog("Copiando/creando " + dirPath + " ->" + dirDestino)
                        copyFilesWithProgress(dirPath, dirDestino) 
                        # shutil.copytree(dirPath, dirDestino)
                except Exception as e:
                    writeLog("Error: " + str(e))

    writeLog(str(copiados) + " de " + str(cont) + " directorios copiados")
    print("\n")

    # Backup Log
    origen = "V:\\BackupEpsas\\P01"
    cont = 0
    copiados = 0
    ignorar = [".ora", ".log", ".sap", ".ini"]
    destino = "D:\\oracle\P01\\sapbackup\\BackupEpsas\\P01"
    writeLog("Backup logs " + origen + " -> " + destino)

    for (root,dirs,files) in os.walk(origen):
        for archivo in files:
            cont += 1
            if Path(archivo).suffix.lower() in ignorar:
                continue
            try:
                archOrigen = os.path.join(root,archivo)
                ctimeOrigen = os.stat(archOrigen).st_ctime
                if datetime.now() > datetime.fromtimestamp(ctimeOrigen) + timedelta(days=10):
                    writeLog("ignorando " + archOrigen)
                    continue

                archDestino = os.path.join(destino,archivo)
                if not os.path.isfile(archDestino) or not filecmp.cmp(archOrigen,archDestino):
                    copiados += 1
                    writeLog("copia de " + archOrigen + " a " + archDestino)
                    shutil.copyfile(archOrigen, archDestino)
            except Exception as e:
                writeLog("Error: " + str(e))

    writeLog(str(copiados) + " de " + str(cont) + " archivos copiados")
    print("[+] Fin sinc. backup" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def copiarAL():
    """ Archive logs """
    
    print("[+] Sincronizando Archive Logs" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    writeLog("Inicio AL")

    # Archivo de Check Sum
    dict={}
    chksm = os.path.join(dirBackup, "sync_chksm.txt")
    if os.path.isfile(chksm) and os.path.getsize(chksm) > 0:
        with open(chksm, mode='rb') as checksum:
            dict = cPickle.load(checksum)

    # Archive logs
    origen = "W:\\"
    cont = 0
    copiados = 0
    destino = "E:\\oracle\\P01\\oraarch"
    writeLog("Archive logs " + origen + " -> " + destino)
    
    for (root,dirs,files) in os.walk(origen):
        for archivo in files:
            cont += 1
            archOrigen = os.path.join(root,archivo)
            archDestino = os.path.join(destino,archivo)
            try:
                if not os.path.isfile(archDestino) or not filecmp.cmp(archOrigen,archDestino): 
                    hashOrigen = md5(archOrigen)
                    copiados += 1
                    writeLog("copia de " + archOrigen + " MD5(" + hashOrigen + ")" )
                        
                    hashDict = dict.get(archDestino, "x")
                    if hashDict == "x":
                        hashDestino = hashOrigen
                    
                    if os.path.isfile(archDestino):
                        hashDestino = md5(archDestino)
                        writeLog("reemplazando " + archDestino + " MD5(" + hashDestino + ")" )

                    dict[archOrigen] = hashDestino
                    shutil.copyfile(archOrigen, archDestino)
            except Exception as e:
                writeLog("Error: " + str(e))

    writeLog(str(copiados) + " de " + str(cont) + " archivos copiados")

    # CHECKSUM
    with open(chksm, mode='wb') as checksum:
        cPickle.dump(dict, checksum)

    print("[+] Fin sinc. Archive Logs" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def md5(fname):
    """ Calculo de hash """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def writeLog(log):
    logFile = os.path.join(dirBackup, "sync_" + datetime.now().strftime("%Y%m%d")) + ".log"
    fh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logFile, mode='a') as logWriter:
        if len(log) > 0:
            logWriter.write(fh + " " + log + "\n")
        else:
            logWriter.write("\n")

def main():
    try:
        fh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[+] Inicio de sincronización de backup y archive logs " + fh)
        writeLog("")
        writeLog("Inicio de programa")
        copiarBK()
        lapso = 300 # 5 minutos
        while True:
            time.sleep(lapso)
            hoy = datetime.now()
            # Horarios
            h1 = hoy.replace(hour=5, minute=0, second=0, microsecond=0)
            h2 = hoy.replace(hour=6, minute=0, second=0, microsecond=0)
            h3 = hoy.replace(hour=23, minute=0, second=0, microsecond=0)

            if datetime.today().weekday() == 6 and datetime.now() <= h1 and datetime.now() + timedelta(seconds=lapso) >= h1:
                # Domingos
                copiarBK()
            elif (datetime.now() <= h2 and datetime.now() + timedelta(seconds=lapso) >= h2) or (datetime.now() <= h3 and datetime.now() + timedelta(seconds=lapso) >= h3):
                # Dos veces al día
                copiarAL()

    except KeyboardInterrupt:
        fh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[-] Interrumpido por el usuario " + fh)
        writeLog("Interrumpido por el usuario")


if __name__ == "__main__":
    main()

