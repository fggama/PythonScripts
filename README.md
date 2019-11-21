# PythonScripts
> Algunos scripts Python para realizar copias de seguridad incrementales en Windows, los utilizo todos los días

* Backup Incremental de Archivos (CopiaArchivos.py)
* Restaura archivos desde la estructura del Backup Incremental (RestauraArchivos.py)
* Busca archivos en los archivos de Backup (BuscaArchivos.py)

## CopiaArchivos.py
```
CopiaArchivos.py -d "archivo de detalle" -2 -h
```
_-2 crea archivos zip con el path relativo_

_-h ayuda_

## RestauraArchivos.py
```
RestauraArchivos.py -o "restaurar desde" -d "restaurar a" -x "extraer el direcorio o archivo"'
```
_-h ayuda_

## BuscaArchivos.py
```
BuscaArchivos.py -o "buscar en" -b "direcorio o archivo" -s
```
_-s (opcional) desplegar sin paginacion_

_-h ayuda_
  
---
### Meta

Freddy Garcia Massa – [@FreddyGMassa](https://twitter.com/FreddyGMassa) – fggama@gmail.com
