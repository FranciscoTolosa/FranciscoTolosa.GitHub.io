import http.client
import json
import pandas as pd
from datetime import datetime

conn = http.client.HTTPSConnection("idealista2.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "2c0bf225femsh159a2e3f8d35130p1decfdjsn6b73ccafdae0",
    'x-rapidapi-host': "idealista2.p.rapidapi.com"
}

# Lista para almacenar todas las propiedades
all_properties = []
page = 1
total_pages = 1  # Se actualizará con la primera respuesta

# Pedir al usuario el término de búsqueda
termino_busqueda = input("Introduce el término de búsqueda para la ubicación: ")

# Usar el término de búsqueda en la URL
conn.request("GET", f"/auto-complete?prefix={termino_busqueda}&country=es", headers=headers)

res = conn.getresponse()
data = res.read()
resultados = json.loads(data.decode("utf-8"))

# Print the raw data to see its structure
print("Raw data:", resultados)

print("\nResultados encontrados:")
if isinstance(resultados, dict) and 'locations' in resultados:
    # Enumerar las ubicaciones
    for i, ubicacion in enumerate(resultados['locations'], 1):
        if isinstance(ubicacion, dict) and 'name' in ubicacion:
            print(f"{i}. {ubicacion['name']}")
    
    # Pedir al usuario que seleccione un número
    try:
        seleccion = int(input("\nSelecciona el número de la ubicación deseada: "))
        if 1 <= seleccion <= len(resultados['locations']):
            ubicacion_seleccionada = resultados['locations'][seleccion - 1]
            print(f"\nHas seleccionado: {ubicacion_seleccionada['name']}")
            location_id = ubicacion_seleccionada['locationId']
            print(f"LocationID: {location_id}")
        else:
            print("Número fuera de rango. Por favor, selecciona un número válido.")
    except ValueError:
        print("Por favor, introduce un número válido.")
else:
    print("\nNo se pudieron procesar los resultados. Formato de respuesta inesperado.")

# Usar el locationId seleccionado en la solicitud de propiedades
while page <= total_pages:
    conn.request("GET", f"/properties/list?numPage={page}&locationId={location_id}&sort=asc&locale=es&operation=rent&country=es&propertyType=bedrooms", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    # Convertir la respuesta JSON a un diccionario de Python
    json_data = json.loads(data.decode("utf-8"))
    
    # Actualizar total_pages en la primera iteración
    if page == 1:
        total_pages = json_data.get('totalPages', 1)
        print(f"Total de páginas a procesar: {total_pages}")
    
    # Extraer la lista de propiedades y añadirla a la lista general
    properties = json_data.get('elementList', [])
    all_properties.extend(properties)
    
    print(f"Procesada página {page} de {total_pages}")
    page += 1

# Crear un DataFrame con todas las propiedades
df = pd.DataFrame(all_properties)

# Crear una nueva columna 'zona' que use 'district' si está disponible, si no, usa 'municipality'
df['zona'] = df['district'].fillna(df['municipality'])

# Calcular el precio medio y la varianza por zona, solo para zonas con al menos 3 precios
precio_stats_zona = df.groupby('zona').agg({
    'price': ['count', 'mean', 'var']
}).reset_index()

# Renombrar las columnas para mayor claridad
precio_stats_zona.columns = ['zona', 'count', 'precio_medio', 'varianza']

# Filtrar solo las zonas con al menos 3 precios
precio_stats_zona = precio_stats_zona[precio_stats_zona['count'] >= 3]

# Eliminar la columna 'count' que ya no necesitamos
precio_stats_zona = precio_stats_zona.drop('count', axis=1)

# Generar un nombre para el nuevo archivo Excel
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename_medias = f'precios_medios_zona_{timestamp}.xlsx'

# Guardar el nuevo DataFrame en un archivo Excel
precio_stats_zona.to_excel(filename_medias, index=False)

print(f"\nArchivo Excel '{filename_medias}' generado correctamente con los precios medios y varianzas por zona")

# Reiniciar variables para la nueva búsqueda
all_properties = []
page = 1
total_pages = 1

# Buscar apartamentos en alquiler
while page <= total_pages:
    conn.request("GET", f"/properties/list?numPage={page}&locationId={location_id}&sort=asc&locale=es&operation=rent&country=es", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    json_data = json.loads(data.decode("utf-8"))
    
    if page == 1:
        total_pages = json_data.get('totalPages', 1)
        print(f"Total de páginas a procesar para alquiler: {total_pages}")
    
    properties = json_data.get('elementList', [])
    all_properties.extend(properties)
    
    print(f"Procesada página {page} de {total_pages}")
    page += 1

# Crear DataFrame con las propiedades de alquiler
df_alquiler = pd.DataFrame(all_properties)

# Filtrar apartamentos con 3 o más habitaciones
df_alquiler = df_alquiler[df_alquiler['rooms'] >= 3]

# Crear columna zona igual que antes
df_alquiler['zona'] = df_alquiler['district'].fillna(df_alquiler['municipality'])

# Leer el Excel de precios medios generado anteriormente
precio_stats_zona = pd.read_excel(filename_medias)

# Hacer merge con los precios medios
df_alquiler_con_medias = df_alquiler.merge(
    precio_stats_zona,
    left_on='zona',
    right_on='zona',
    how='left'
)

# Generar nombre para el nuevo archivo
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename_alquiler = f'alquiler_3rooms_{timestamp}.xlsx'

# Guardar el DataFrame en Excel
df_alquiler_con_medias.to_excel(filename_alquiler, index=False)

print(f"\nArchivo Excel '{filename_alquiler}' generado correctamente con {len(df_alquiler_con_medias)} propiedades de alquiler con 3 o más habitaciones")Cordo