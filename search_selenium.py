from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Usar WebDriver Manager para instalar y configurar automáticamente ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Abrir Google
driver.get("https://www.google.com")

# Buscar "Rascuache"
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Rascuache")
search_box.send_keys(Keys.RETURN)

# Esperar unos segundos para ver resultados
time.sleep(5)

# Cerrar el navegador
driver.quit()
