from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import csv

def limpiar_precio(precio_raw):
    match = re.search(r'\$([\d,]+)(\d{2})$', precio_raw.replace(" ", ""))
    if match:
        return f"${match.group(1)}.{match.group(2)}"
    return precio_raw

# 1. Inicializar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.liverpool.com.mx")
time.sleep(3)

# 2. Aceptar cookies si aparecen
try:
    aceptar_cookies = driver.find_element(By.ID, "cookie-policy-info-accept")
    aceptar_cookies.click()
except:
    pass

# 3. Buscar laptops
search_box = driver.find_element(By.ID, "mainSearchbar")
search_box.send_keys("laptop")
search_box.send_keys(Keys.RETURN)
time.sleep(5)

# 4. Obtener los contenedores de productos
productos = driver.find_elements(By.CLASS_NAME, "m-product__card")[:10]

print("Primeras 10 laptops:\n")

for producto in productos:
    try:
        nombre = producto.find_element(By.CLASS_NAME, "a-card-description").text
    except:
        nombre = "Nombre no encontrado"

    try:
        precio = limpiar_precio(producto.find_element(By.CLASS_NAME, "a-card-price").text)


    except:
        precio = "Precio no encontrado"

    print(f"🖥️ {nombre} - 💲{precio}")

# ... Todo tu código igual hasta el print(f"🖥️ {nombre} - 💲{precio}")

# Creamos listas para guardar los datos
nombres = []
precios = []

for producto in productos:
    try:
        nombre = producto.find_element(By.CLASS_NAME, "a-card-description").text
    except:
        nombre = "Nombre no encontrado"

    try:
        precio = limpiar_precio(producto.find_element(By.CLASS_NAME, "a-card-price").text)
    except:
        precio = "Precio no encontrado"

    nombres.append(nombre)
    precios.append(precio)

    print(f"🖥️ {nombre} - 💲{precio}")

# Guardamos en CSV
with open("laptops_liverpool.csv", mode="w", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(["Nombre", "Precio"])
    for nombre, precio in zip(nombres, precios):
        escritor.writerow([nombre, precio])

# Cerrar navegador
driver.quit()

