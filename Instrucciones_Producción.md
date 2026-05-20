# 🚀 Guía de Despliegue en Producción (AWS EC2 / VPS)

Esta guía detalla paso a paso cómo poner en producción la aplicación **combustible_ybarato.es** en un servidor virtual privado (VPS) gratuito de Amazon (AWS EC2) o cualquier otro servidor Linux (Ubuntu/Debian).

---

## ⚠️ Requisito Indispensable en AWS: Abrir Puertos

Por defecto, AWS bloquea todo el tráfico entrante salvo el puerto 22 (SSH). Para permitir que los usuarios accedan a tu aplicación web, debes abrir el puerto adecuado en la consola de AWS:

1. Ve a la consola de **AWS EC2** y selecciona tu instancia.
2. En la pestaña inferior, ve a **Security (Seguridad)** y haz clic en tu **Security Group (Grupo de Seguridad)**.
3. Haz clic en **Edit inbound rules (Editar reglas de entrada)**.
4. Añade una nueva regla según la opción de despliegue que elijas:
   * **Para Opción 1 (Docker en puerto 80):**
     * **Tipo:** HTTP
     * **Puerto:** 80
     * **Origen:** Cualquier lugar IPv4 (`0.0.0.0/0`)
   * **Para Opción 2 (Servicio Nativo en puerto 8501):**
     * **Tipo:** TCP personalizado
     * **Puerto:** 8501
     * **Origen:** Cualquier lugar IPv4 (`0.0.0.0/0`)
5. Haz clic en **Save rules (Guardar reglas)**.

---

## Opción 1: Despliegue con Docker (Recomendado)

Dado que la aplicación incluye un `Dockerfile` optimizado, esta es la forma más limpia y rápida de desplegarla. No necesitas configurar versiones de Python o dependencias locales en el servidor.

### 1. Conexión al VPS mediante SSH
```bash
ssh -i "tu_clave.pem" ubuntu@tu_ip_publica_aws
```

### 2. Instalación de Docker en el servidor
Si es la primera vez que usas Docker en el VPS, ejecútalo para instalarlo:
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker

# Opcional: Permitir ejecutar docker sin usar sudo
sudo usermod -aG docker $USER
```
*(Si ejecutas el último comando de `usermod`, cierra sesión con `exit` y vuelve a conectarte por SSH para que se aplique).*

### 3. Descargar el código
Clona tu repositorio de GitHub en la carpeta de tu preferencia en el servidor:
```bash
git clone https://github.com/joerqpongo/combustible_ybarato.git
cd combustible_ybarato
```

### 4. Construir la imagen de Docker
```bash
docker build -t combustible-app .
```

### 5. Iniciar el contenedor en producción
Ejecuta la aplicación mapeando el puerto interno `8501` de Streamlit al puerto HTTP estándar `80` del VPS. Esto permite que accedan solo escribiendo la IP pública en el navegador:
```bash
docker run -d \
  --name combustible-buscador \
  -p 80:8501 \
  --restart always \
  combustible-app
```

---

## Opción 2: Despliegue Nativo como Servicio del Sistema (Systemd)

Si prefieres ejecutar el programa directamente sobre el sistema operativo sin usar contenedores, la mejor práctica en Linux es crear un servicio que se levante automáticamente si el servidor se reinicia o si el proceso falla.

### 1. Descargar el código e instalar entorno virtual
```bash
git clone https://github.com/joerqpongo/combustible_ybarato.git
cd combustible_ybarato

# Crear e instalar dependencias en entorno virtual de Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Crear el archivo del Servicio
Crea un archivo de configuración del sistema para el servicio:
```bash
sudo nano /etc/systemd/system/combustible.service
```

Pega el siguiente contenido en el editor. **Nota:** Si tu usuario de acceso no es `ubuntu` o clonaste el proyecto en otra ruta, ajusta los valores de `User`, `WorkingDirectory` y `ExecStart` correspondientemente:

```ini
[Unit]
Description=Buscador de Combustible Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/combustible_ybarato
ExecStart=/home/ubuntu/combustible_ybarato/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
*(Guarda con `Ctrl+O`, presiona `Enter` y sal con `Ctrl+X`)*.

### 3. Habilitar e Iniciar el Servicio
```bash
# Recargar systemd para detectar el nuevo servicio
sudo systemctl daemon-reload

# Habilitar el servicio para que arranque solo al encender el VPS
sudo systemctl enable combustible

# Iniciar el servicio inmediatamente
sudo systemctl start combustible
```

---

## 🛠️ Comandos Útiles de Mantenimiento

### Si usas Docker (Opción 1):
* **Ver estado del contenedor:** `docker ps`
* **Ver logs de la aplicación:** `docker logs -f combustible-buscador`
* **Detener la app:** `docker stop combustible-buscador`
* **Actualizar a la última versión de GitHub:**
  ```bash
  git pull
  docker build -t combustible-app .
  docker rm -f combustible-buscador
  docker run -d --name combustible-buscador -p 80:8501 --restart always combustible-app
  ```

### Si usas Servicio Nativo (Opción 2):
* **Ver estado del servicio:** `sudo systemctl status combustible`
* **Ver logs de la aplicación:** `journalctl -u combustible.service -f`
* **Detener la app:** `sudo systemctl stop combustible`
* **Actualizar a la última versión de GitHub:**
  ```bash
  git pull
  source venv/bin/activate
  pip install -r requirements.txt
  sudo systemctl restart combustible
  ```
