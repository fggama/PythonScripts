import getopt
import sys
import os
import hashlib
import pickle as cPickle
import zipfile
from datetime import datetime
from pathlib import Path
from msvcrt import getch

timestampStr = datetime.now().strftime("%Y-%m-%d_%H-%M")
archivoActual = ""
versionZIP = 0
infoExt = False
key = 0
paginar = True
filas = 25
columnas = 80

def copiar(origen, destino, ignorar):
    """Ejecuta la copia: origen -> destino"""
    dict={}

    destino.mkdir(parents=True, exist_ok=True)
    print(f'[+] {origen}->{destino.absolute()}')
    print(f'\t{ignorar}')
    zipZero = True
 
    os.chdir(destino)

    # Archivo de Check Sum
    chksm = Path.cwd() / "chksm.txt"
    setArchivoActual(chksm)
    if chksm.exists() and os.path.getsize(chksm) > 0:
        with open(chksm,mode='rb') as checksum:
            dict = cPickle.load(checksum)

    # Registro de archivos borrados
    setArchivoActual(destino / "remove.txt")
    remove = Path("remove.txt")
    with remove.open(mode='w') as rem:
        for k, v in list(dict.items()):
            if(not os.path.exists(k)):
                try:
                    rem.write(f'{k}\n')
                except:
                    print(f'[-] {k}\n')

                del dict[k]

    # Escribe archivo ZIP
    # Registro de archivos ignorados
    setArchivoActual(f"ignore:{destino / 'ignore.txt'}")
    ign = Path("ignore.txt")
    ignore = open(ign, mode='w')
    delta = zipfile.ZipFile(Path("delta.zip"), 'w')
    num = sum([len(files) for r, d, files in os.walk(origen)])
    cont = 0
    copiados = 0
    for (root,dirs,files) in os.walk(origen):
        if os.path.dirname(root) == os.path.dirname(origen):
            dirs[:] = [d for d in dirs if d not in ignorar]

        for archivo in files:
            if archivo in ignorar:
                continue

            cont += 1
            archParaZip = os.path.join(root, archivo)
            progreso(num, cont, str(archParaZip))
            setArchivoActual(archParaZip)
            f_temp = open(archParaZip,'rb')
            content = f_temp.read()
            m = hashlib.md5()
            m.update(content)
            f_temp.close()
            setArchivoActual(f"delta:{delta.filename}")
            
            try:
                if(dict[archParaZip] != m.hexdigest()):
                    zipZero = False
                    delta.write(archParaZip, os.path.join(setDir(root, origen), archivo))
                    dict[archParaZip] = m.hexdigest()
                    copiados += 1
                else:
                    ignore.write(f'{str(archParaZip)}\n')

            except KeyError:
                zipZero = False
                delta.write(archParaZip, os.path.join(setDir(root, origen),archivo))
                dict[archParaZip] = m.hexdigest()
                copiados += 1
    
    delta.close()
    ignore.close()
    setArchivoActual(os.path.join(destino, "chksm.txt"))
    with  open("chksm.txt",mode='wb') as checksum:
        cPickle.dump(dict,checksum)

    if cont < num and cont > 0:
        progreso(num,num,'')
    print(f"[+] # archivos copiados: {copiados}\n")
    
    deltazip = Path("delta.zip")
    if zipZero:
        try:
            deltazip.unlink()
        except:
            pass
    else:
        deltazip.rename(Path(f"{timestampStr}.zip"))

def setDir(root, dir_origen):
    """ Direccion absoluta o relativa """
    if versionZIP == 1:
        return root.replace(str(dir_origen),"")
    else:
        return root

def progreso(total, i, archivo):
    """Despliega el progreso de la ejecución"""
    global columnas
    try:
        incre = int(50.0 / total * i)
        archivo.replace("\n","")
        espacios = columnas - len(archivo) - 20
        if espacios < 0:
            espacios = 0
            archivo = archivo[:columnas - 20]

        if i < total:
            print('\r| %d%%  |%s' % (2*incre, ' '*5 + archivo + ' '*espacios), end="\r")
            # print('\r| %d%%  |%s' % (2*incre, ' '*5 + archivo), end="\r")
            # sys.stdout.write('\r' + '| %d%%  |%s' % (2*incre,' '*5 + archivo + ' '*espacios),)
        else:
            sys.stdout.write('\r|%d%%  |%s' % (100,' '*5 + 'Finalizado' + ' '*90))
            sys.stdout.write('\n')
            print(f'[+] # archivos procesados: {total}')
    except:
        print("[-] Info:", str(sys.exc_info()))
        
    sys.stdout.flush()

def setArchivoActual(nombre):
    """Registra el nombre del archivo en proceso"""
    global archivoActual     
    archivoActual = nombre

def listaArchivos(destino, nivel):
    global key
    global numArchivos
    global paginar
    cont = 0
    dirname = ''
    zipArchivos = Path(destino).glob("*.zip")

    for zipArchivo in [x for x in zipArchivos if x.is_file()]:
        print(f"[*] Archivo: {zipArchivo}")
        with zipfile.ZipFile(zipArchivo) as esteZip:
            dict = {}
            for name in esteZip.namelist():
                i = 0
                for h in range(0,nivel):
                    i = name.find('/',i)
                    if i >= 0:
                        dirname = name[0:i+1]
                        if dirname not in dict:
                            dict[dirname] = dirname
                            print ('\t'*h + f'\t{dirname}')
                            cont += 1
                        i += 1
                    else:
                        break

                c = name.count("/")
                if c < nivel:
                    info = esteZip.getinfo(name)
                    namefile = info.filename.replace(dirname,'')
                    print ('\t'*h + f'\t{namefile}')
                    cont += 1
                    if infoExt:
                        #print ('\t'*h + '\t\tComment:\t', info.comment)
                        print ('\t'*h + '\t\tModified:\t', datetime(*info.date_time))
                        #print ('\t'*h + '\t\tSystem:\t\t', info.create_system, '(0 = Windows, 3 = Unix)')
                        print ('\t'*h + '\t\tZIP version:\t', info.create_version)
                        print ('\t'*h + '\t\tCompressed:\t', info.compress_size, 'bytes')
                        print ('\t'*h + '\t\tUncompressed:\t', info.file_size, 'bytes')
                        cont += 6

                if paginar and cont >= filas - 1:
                    cont = 1
                    print("presione una tecla para continuar, ESC para salir, C continuar sin paginacion...")
                    key = ord(getch())
                    if key == 67 or key == 99:
                        paginar = False
                    if key == 27:
                        break
        if key == 27:
            break

def get_windows_terminal():
    from ctypes import windll, create_string_buffer
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
 
    if not res: return 
 
    import struct
    (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
    global columnas 
    columnas = right - left + 1
    global filas
    filas = bottom - top + 1
    return

def printInstrucciones():
     print ('\tusar: CopiaArchivos.py -d <archivo de detalle> [-a] [-l <nivel>]')
     print ('\t\tRealiza la copia y compresión (archivos ZIP) en forma "incremental", de los directorios especificados en')
     print ('\t\tel archivo de "detalle" con el formato: "directorio_origen, drectorio_destino_disco_actual",')
     print ('\t\tpara ignorar la copia de un directorio se debe crear un archivo de texto vacio con el nombre ".caignore"')
     print ('\n\t\t-h\tAyuda')
     print ('\t\t-d\tArchivo de detalle, donde se especifica los directorios Origen y Destino de la copia')
     print ('\t\t-l\tListar los elementos copiados, hasta el nivel especificado')
     print ('\t\t-i\tListar con informacion extendida')
     print ('\t\t-a\tUtilizar rutas absolutas en el archivo ZIP')
     print ('  ej:   CopiaArchivos.py -d detalle.txt [-a] [-l <nivel>]')

def main(argv):
    archiDetalle = "detalle-epsas.txt"
    nivel = ""
    
    global versionZIP
    global infoExt
    global columnas, filas

    try:
        opts, args = getopt.getopt(argv,"haid:l:")
    except getopt.GetoptError:
        print ('[-] Error vea las instrucciones.')
        printInstrucciones()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            printInstrucciones()
            sys.exit()
        elif opt in ("-d"):
            archiDetalle = arg
        elif opt in ("-a"):
            versionZIP = 0
        elif opt in ("-i"):
            infoExt = True
        elif opt in ("-l"):
            nivel = arg

    if len(archiDetalle) == 0:
        printInstrucciones()
        sys.exit(2)
    
    size = os.get_terminal_size()
    filas = size.lines
    columnas = size.columns

    # get_windows_terminal()
    origen = ""
    destino = ""
    ignorar = []
    try:
        raizBackup = Path(Path.cwd())
        print(f"\n[+] Directorio actual: {Path.cwd()}\n")
        if not Path(archiDetalle).exists():
            raise Exception(f'[-] No se encuentra el archivo {archiDetalle}')
    
        archiDetalle = Path(archiDetalle)
        setArchivoActual(archiDetalle)
        detalle = Path(archiDetalle).read_text()
        lista = detalle.split('\n')
        cont = 0
        for linea in lista:
            if len(linea) <= 1 or linea.startswith("#") or ',' not in linea:
                continue
    
            dirs = linea.replace('/','\\').replace('[','').replace(']','').rstrip().split(",")
            if (len(dirs) < 3):
                continue
  
            cont +=1
            origen = Path(dirs[0].strip())
            destino = Path(dirs[1].strip())
            ignorar = dirs[2:]
        
            if len(nivel) > 0:
                listaArchivos(destino, int(nivel))
                if key == 27:
                    break
            else:
                if not origen.is_dir():
                    print(f"[-] No existe el directorio origen: {origen} (ignorado)")
                else:
                    print(f"{cont}/{len(lista)}")
                    copiar(origen, destino, ignorar)

            os.chdir(raizBackup)

        if len(nivel) == 0:
            print("[+] Copia Finalizada!")
    except:
        print("[-] Exception")
        print("\tDetalle del proceso ")
        print(f"\t   origen: {origen}")
        print(f"\t  destino: {destino}")
        print(f"\t  archivo: {archivoActual}")
        print("\tInfo:", str(sys.exc_info()))


if __name__ == "__main__":
    main(sys.argv[1:])

