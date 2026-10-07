import sys
import time

# Compatibilidad con la consola de Windows para caracteres y emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def crear_driver_avanzado(headless: bool = False) -> webdriver.Chrome:
    """Configuración avanzada de Google Chrome con Selenium."""
    chrome_options = Options()

    # Rendimiento y estabilidad
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if headless:
        chrome_options.add_argument("--headless=new")

    # Evasión de detección de automatización (anti-bot)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # User Agent estándar
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


def ejecutar_prueba_login(usuario: str, clave: str, headless: bool = False):
    print("=" * 60)
    print("INICIANDO PRUEBA AUTOMATIZADA DE LOGIN - FIDEINEXUS")
    print("=" * 60)

    driver = None
    try:
        # [Paso 1] Abrir Navegador
        print("\n[Paso 1] Abrir Navegador (configuracion avanzada)...")
        driver = crear_driver_avanzado(headless=headless)
        wait = WebDriverWait(driver, 15)

        # [Paso 2] Abrir Login
        login_url = "https://lab.vallegrande.edu.pe/fideiNexus/login"
        print(f"[Paso 2] Abrir Login: {login_url}")
        driver.get(login_url)
        wait.until(EC.visibility_of_element_located((By.ID, "email")))
        print(f"         Pagina cargada exitosamente: '{driver.title}'")

        # [Paso 3] Ingresar Usuario
        print(f"[Paso 3] Ingresar Usuario: {usuario}")
        campo_usuario = wait.until(EC.element_to_be_clickable((By.ID, "email")))
        campo_usuario.clear()
        campo_usuario.send_keys(usuario)

        # [Paso 4] Ingresar Clave
        print("[Paso 4] Ingresar Clave: ********")
        campo_clave = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        campo_clave.clear()
        campo_clave.send_keys(clave)

        # [Paso 5] Clic Ingresar
        print("[Paso 5] Clic Ingresar (boton de inicio de sesion)...")
        boton_ingresar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        boton_ingresar.click()

        # [Paso 6] Obtener Mensaje
        print("[Paso 6] Obtener Mensaje y verificar respuesta...")
        mensaje_obtenido = None

        try:
            # Esperar redirección fuera del login (Login Exitoso)
            wait.until(lambda d: "/login" not in d.current_url)
            nueva_url = driver.current_url

            # Obtener encabezado principal del módulo cargado
            try:
                def header_cargado(d):
                    for h in d.find_elements(By.TAG_NAME, "h1"):
                        texto = h.text.strip()
                        if texto and "cargando" not in texto.lower():
                            return texto
                    return False

                encabezado = wait.until(header_cargado)
            except TimeoutException:
                encabezado = "Panel Principal"

            mensaje_obtenido = f"LOGIN EXITOSO | Modulo: '{encabezado}' | URL destino: {nueva_url}"
            print(f"         [OK] {mensaje_obtenido}")

        except TimeoutException:
            # Si no redirigió, capturar alertas o mensajes de error
            posibles_selectores = [
                "[role='alert']", ".toast", ".swal2-html-container",
                ".alert-danger", ".error-message", "div.text-red-500",
                "span.text-red-500", "p.text-red-500"
            ]

            texto_error = ""
            for selector in posibles_selectores:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elementos:
                    if elem.text.strip():
                        texto_error = elem.text.strip()
                        break
                if texto_error:
                    break

            if texto_error:
                mensaje_obtenido = f"ERROR DE LOGIN | Mensaje en pantalla: {texto_error}"
                print(f"         [ALERTA] {mensaje_obtenido}")
            else:
                mensaje_obtenido = f"SIN REDIRECCION | Permanece en: {driver.current_url}"
                print(f"         [INFO] {mensaje_obtenido}")

        # Guardar captura de evidencia
        driver.save_screenshot("resultado_login.png")
        print("         [EVIDENCIA] Captura guardada como 'resultado_login.png'")

        print("\n" + "=" * 60)
        print("RESULTADO FINAL: " + mensaje_obtenido)
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Ocurrio un error inesperado: {e}")
        if driver:
            driver.save_screenshot("error_login.png")
    finally:
        if driver:
            print("\nCerrando navegador...")
            driver.quit()
            print("Prueba finalizada.")


if __name__ == "__main__":
    USUARIO_TEST = "testeo@gmail.com"
    CLAVE_TEST = "12345678"

    ejecutar_prueba_login(USUARIO_TEST, CLAVE_TEST, headless=False)
