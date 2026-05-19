# ⛽ combustible_ybarato.es

Aplicación Streamlit para buscar las gasolineras más baratas en España.  
Datos oficiales del **Geoportal de Gasolineras** (Ministerio para la Transición Ecológica).

---

## 🚀 Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

La app estará disponible en `http://localhost:8501`.

---

## 🖥️ Despliegue en VPS con `nohup`

```bash
# 1. Clonar/subir el proyecto en el servidor
cd /opt/combustible_ybarato

# 2. Instalar dependencias en entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Ejecutar en segundo plano con nohup
nohup streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  > logs/app.log 2>&1 &

echo "PID: $!" > app.pid
echo "Aplicación iniciada. Ver logs con: tail -f logs/app.log"
```

Para detenerla:
```bash
kill $(cat app.pid)
```

---

## 🐳 Despliegue con Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true"]
```

### Comandos Docker

```bash
# Construir imagen
docker build -t combustible-ybarato .

# Ejecutar contenedor
docker run -d \
  --name combustible-ybarato \
  --restart unless-stopped \
  -p 8501:8501 \
  combustible-ybarato

# Ver logs en tiempo real
docker logs -f combustible-ybarato

# Detener y eliminar
docker stop combustible-ybarato && docker rm combustible-ybarato
```

### docker-compose.yml (opcional)

```yaml
version: "3.9"
services:
  combustible:
    build: .
    container_name: combustible-ybarato
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./cache:/app/cache
```

```bash
docker compose up -d
```

---

## 🔧 Variables de entorno opcionales

| Variable | Descripción | Defecto |
|---|---|---|
| `STREAMLIT_SERVER_PORT` | Puerto del servidor | `8501` |
| `STREAMLIT_SERVER_ADDRESS` | Dirección de escucha | `0.0.0.0` |

---

## 📌 Notas técnicas

- Los datos se actualizan automáticamente cada día a las **06:00 AM** si hay una nueva versión.
- El fichero XLS se descarga de: `https://geoportalgasolineras.es/geoportal/resources/files/preciosEESS_es.xls`
- El geocodificador usa **Nominatim (OpenStreetMap)** para convertir nombres de ciudad a coordenadas.
- La detección de GPS automática requiere `streamlit-js-eval` y que el navegador tenga permisos de ubicación.
