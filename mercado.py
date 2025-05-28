from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurar el driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar sin interfaz gráfica (opcional)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

producto = "Audífonos Bluetooth"

def obtener_precio_mercado_libre():
    url = 'https://www.mercadolibre.com.mx/'
    driver.get(url)

    # Buscar el producto
    buscador = wait.until(EC.presence_of_element_located((By.NAME, 'as_word')))
    buscador.clear()
    buscador.send_keys(producto)
    buscador.send_keys(Keys.RETURN)

    try:
        # Esperar a que los productos carguen
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ui-search-result__content")))
        productos = driver.find_elements(By.CLASS_NAME, "ui-search-result__content")
        if not productos:
            return "No encontrado"

        primer_producto = productos[0]

        # Extraer el precio
        try:
            precio_entero = primer_producto.find_element(By.CLASS_NAME, "andes-money-amount__fraction").text
            precio_decimal = primer_producto.find_element(By.CLASS_NAME, "andes-money-amount__cents").text
            precio = f"${precio_entero}.{precio_decimal}"
        except:
            # En caso de que el precio no tenga decimales
            precio = f"${primer_producto.find_element(By.CLASS_NAME, 'andes-money-amount__fraction').text}"

    except Exception as e:
        print(f"Error en Mercado Libre: {e}")
        precio = "No encontrado"

    return precio

# Ejecutar la función y obtener el precio
precio_mercado_libre = obtener_precio_mercado_libre()
driver.quit()

print(f"Precio en Mercado Libre: {precio_mercado_libre}")
