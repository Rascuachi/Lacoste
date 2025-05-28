from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
import re
import time

DEBUG = True  # Cambia a False para no imprimir errores

producto = 'Polo Blanca Lacoste talla M'

def formatear_precio(precio_raw):
    """
    Formatea una cadena de texto para extraer un precio en formato $X.YY.
    Maneja diferentes formatos de entrada (con comas, con centavos como sup, etc.).
    """
    if not isinstance(precio_raw, str):
        return "No encontrado"

    # Elimina el signo de dólar, comas de miles y cualquier texto no numérico excepto el punto.
    precio = re.sub(r'[^\d.]', '', precio_raw)

    if not precio:
        return "No encontrado"

    # Asegura que haya dos decimales si no los tiene o si son solo un dígito
    if '.' not in precio:
        # Si el número no tiene punto, y es suficientemente largo, asume los últimos dos son centavos
        if len(precio) > 2:
            precio = f"{precio[:-2]}.{precio[-2:]}"
        else: # Si es 12 o 1, asume 12.00 o 1.00
            precio += '.00'
    else:
        partes = precio.split('.')
        if len(partes) > 2: # Si hay múltiples puntos (e.g., 1.234.56)
            precio = "".join(partes[:-1]) + "." + partes[-1]
            partes = precio.split('.')

        if len(partes[1]) == 1: # Si solo hay un decimal (e.g., "123.4")
            precio += '0'
        elif not partes[1]: # Si solo hay un punto al final (e.g., "123.")
            precio += '00'
        else: # Asegura que haya solo dos decimales
            precio = f"{partes[0]}.{partes[1][:2]}"

    return f"${precio}"

def crear_driver(headless_mode=True):
    """
    Crea y configura una instancia del driver de Chrome.
    Argumento headless_mode: True para ejecutar en modo headless, False para ver el navegador.
    """
    options = webdriver.ChromeOptions()
    if headless_mode:
        options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080") # Tamaño de ventana para evitar responsividad
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3") # Suprime mensajes de error del driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# --- Funciones para obtener precios de cada tienda ---

def obtener_precio_liverpool(driver, wait):
    url = 'https://www.liverpool.com.mx/tienda/home'
    driver.get(url)

    try:
        # Intenta aceptar cookies. Si no aparece, ignora el error.
        aceptar_cookies = wait.until(EC.element_to_be_clickable((By.ID, "cookie-policy-info-accept")))
        aceptar_cookies.click()
        time.sleep(1) # Pequeña pausa para que el banner desaparezca
    except (NoSuchElementException, TimeoutException):
        if DEBUG:
            print("Liverpool: No se encontró el botón de aceptar cookies o ya fue aceptado.")
        pass

    try:
        # Utiliza un selector más robusto para la barra de búsqueda si 'mainSearchbar' falla.
        buscador = wait.until(EC.presence_of_element_located((By.ID, 'mainSearchbar')))
        
        buscador.clear()
        buscador.send_keys(producto)
        buscador.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "m-product__card")))
        productos = driver.find_elements(By.CLASS_NAME, "m-product__card")

        if not productos:
            if DEBUG:
                print("Liverpool: No se encontraron productos.")
            return "No encontrado"

        primer_producto = productos[0]
        precio_texto = "No encontrado"

        # Intentar varios selectores para el precio
        # PRIORIZAR precio con descuento, luego precio normal
        posibles_selectores = [
            (By.CSS_SELECTOR, ".a-card-discount"), # Precio con descuento
            (By.CSS_SELECTOR, ".a-price"),        # Precio normal
            (By.CSS_SELECTOR, ".a-product-price") # Otro posible selector de precio
        ]

        for by_type, selector in posibles_selectores:
            try:
                precio_element = primer_producto.find_element(by_type, selector)
                # Liverpool a veces pone los centavos en un <sup>. Extraer el texto completo.
                precio_texto = precio_element.text.strip()
                if precio_texto:
                    break # Si encontramos un precio, salimos del bucle
            except NoSuchElementException:
                continue
        
        # Si el precio incluye un rango (ej. "$2,69000 - $2,79000"), toma solo el primer valor
        if " - " in precio_texto:
            precio_texto = precio_texto.split(" - ")[0]

        return formatear_precio(precio_texto)

    except Exception as e:
        if DEBUG:
            print(f"Liverpool error inesperado: {e}")
        return "No encontrado"

def obtener_precio_amazon(driver, wait):
    url = 'https://www.amazon.com.mx/'
    driver.get(url)

    try:
        buscador = wait.until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        buscador.clear()
        buscador.send_keys(producto)
        buscador.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")))
        
        # Buscar el primer resultado que contenga un precio
        primer_resultado_con_precio = driver.find_element(By.XPATH, "//div[contains(@class, 's-main-slot')]//div[@data-component-type='s-search-result'][.//span[contains(@class, 'a-price')]]")
        
        precio_entero = primer_resultado_con_precio.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        # Los centavos pueden no existir, así que se maneja con try-except
        try:
            precio_decimal = primer_resultado_con_precio.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
        except NoSuchElementException:
            precio_decimal = "00" # Si no hay centavos, asume .00

        precio_raw = f"{precio_entero}.{precio_decimal}"
        return formatear_precio(precio_raw)

    except (NoSuchElementException, TimeoutException) as e:
        if DEBUG:
            print(f"Amazon error: No se encontró el elemento de precio o el resultado de búsqueda: {e}")
        return "No encontrado"
    except Exception as e:
        if DEBUG:
            print(f"Amazon error inesperado: {e}")
        return "No encontrado"

# --- Función principal ---

def main():
    # Se crea UN SOLO driver al inicio de main y se pasa a cada función.
    driver = crear_driver(headless_mode=False) # Puedes cambiar a True para ejecutar sin interfaz
    wait = WebDriverWait(driver, 20) 

    precios = []
    
    print(f"Buscando el producto: '{producto}'\n")

    try:
        precio_liverpool = obtener_precio_liverpool(driver, wait)
        print(f"Precio en Liverpool: {precio_liverpool}")
        precios.append(("Liverpool", producto, precio_liverpool))
    except Exception as e:
        print(f"Error fatal al obtener precio de Liverpool: {e}")
        precios.append(("Liverpool", producto, "Error al obtener"))

    try:
        precio_amazon = obtener_precio_amazon(driver, wait)
        print(f"Precio en Amazon: {precio_amazon}")
        precios.append(("Amazon", producto, precio_amazon))
    except Exception as e:
        print(f"Error fatal al obtener precio de Amazon: {e}")
        precios.append(("Amazon", producto, "Error al obtener"))

    finally:
        driver.quit() # Asegura que el navegador se cierre al final

    # Guardar en CSV
    with open('precios.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Tienda', 'Producto', 'Precio'])
        writer.writerows(precios)

    print("\n✅ Datos guardados en precios.csv")

if __name__ == "__main__":
    main()