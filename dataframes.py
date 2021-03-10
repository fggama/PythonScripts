# establece NaN al leer el archivo
cities=pd.read_html("assests/wikipedia_data.html", na_values=['—'])[1]

# selecciona todas las filas, exceptuando la ultima, y las columnas [0,3,5,6,7,8], borra los NaN en la columna NHL
cities=cities.iloc[:-1,[0,3,5,6,7,8]].dropna(subset=['NHL'])