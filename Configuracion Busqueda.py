import http.client
import json

# Pedir al usuario el término de búsqueda
termino_busqueda = input("Introduce el término de búsqueda para la ubicación: ")

conn = http.client.HTTPSConnection("idealista2.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "2c0bf225femsh159a2e3f8d35130p1decfdjsn6b73ccafdae0",
    'x-rapidapi-host': "idealista2.p.rapidapi.com"
}

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
            print(f"LocationID: {ubicacion_seleccionada['locationId']}")
        else:
            print("Número fuera de rango. Por favor, selecciona un número válido.")
    except ValueError:
        print("Por favor, introduce un número válido.")
else:
    print("\nNo se pudieron procesar los resultados. Formato de respuesta inesperado.")

# Pedir al usuario que elija una ubicación
ubicacion_elegida = input("\nPor favor, introduce la ubicación que deseas seleccionar de la lista anterior: ")