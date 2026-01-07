# 🎓 Monitor de Curso de Verano - UNMSM MAT

Este script monitorea la página de trámites de la **Facultad de Ingeniería de Sistemas e Informática (FISI)** de la UNMSM y envía notificaciones por **Telegram** cuando detecta la disponibilidad del **Curso de Verano**.

## ✨ Características

- 🔐 Login automático con credenciales UNMSM
- 🔑 Obtención de token JWT para API
- 📋 Consulta directa a la API de trámites (sin Selenium ni Puppeteer)
- 🔍 Búsqueda de palabras clave de verano
- 📱 Notificación instantánea por Telegram
- ⏰ Monitoreo continuo cada 5 minutos (configurable)

## 📋 Requisitos

- Python 3.6 o superior
- Módulo `requests` (usualmente preinstalado)

## 🚀 Opción 1: Ejecutar Localmente

```bash
cd /home/iwiels/Documentos/monitoreomat

# Si requests no está instalado:
python3 -m pip install requests

# Ejecutar
python3 monitor.py
```

## ☁️ Opción 2: GitHub Actions (Recomendado)

El repositorio incluye un workflow que ejecuta el monitor **cada 5 minutos** automáticamente.

### Paso 1: Crear repositorio en GitHub

```bash
cd /home/iwiels/Documentos/monitoreomat
git init
git add .
git commit -m "Monitor de curso de verano UNMSM"
git remote add origin https://github.com/TU_USUARIO/monitoreomat.git
git push -u origin main
```

### Paso 2: Configurar Secrets en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Crea estos 4 secrets:

| Nombre | Valor |
|--------|-------|
| `UNMSM_EMAIL` | tu_usuario@unmsm.edu.pe |
| `UNMSM_PASSWORD` | tu_contraseña |
| `TELEGRAM_BOT_TOKEN` | Token de tu bot |
| `TELEGRAM_CHAT_ID` | Tu chat ID |

### Paso 3: Activar el workflow

El workflow se ejecutará automáticamente cada 5 minutos. También puedes ejecutarlo manualmente desde **Actions** → **Monitor Curso de Verano UNMSM** → **Run workflow**.

### ⚠️ Seguridad

- ✅ Las credenciales se almacenan como **GitHub Secrets** (encriptados)
- ✅ El archivo `.env` está en `.gitignore` (nunca se sube)
- ✅ Solo los secrets (encriptados) tienen acceso a las credenciales
- ❌ NUNCA subas credenciales directamente en el código

## ⚙️ Configuración

El archivo `.env` ya está configurado con tus credenciales:

```env
# Credenciales UNMSM
UNMSM_EMAIL=victor.celadita@unmsm.edu.pe
UNMSM_PASSWORD=tu_password

# Telegram Bot
TELEGRAM_BOT_TOKEN=8420887980:AAEgy9z2hTTmoACkiUW3ywAtTI42_dhmmWo
TELEGRAM_CHAT_ID=7880722190

# Intervalo de chequeo en minutos
CHECK_INTERVAL_MINUTES=5

# Código de facultad (20 = FISI)
LOCAL_CODE=20
```

## 🎯 Uso

```bash
# Iniciar el monitor
python3 monitor.py

# Ejecutar en segundo plano (Linux)
nohup python3 monitor.py > monitor.log 2>&1 &

# Ver logs en tiempo real
tail -f monitor.log

# Detener el monitor
pkill -f "python3 monitor.py"
```

## 🔍 Palabras clave buscadas

- verano
- curso verano
- curso de verano
- matricula verano
- matrícula verano
- ciclo verano

## 📊 Estados de trámites

- **DISPONIBLE** (código 1): ✅ Te notificará por Telegram
- **NO DISPONIBLE** (código 0): ❌ Esperando
- **INHABILITADO** (código 2): ❌ Trámite desactivado

## 🤖 Telegram Bot

- Bot: [@VeranoMat22Bot](https://t.me/VeranoMat22Bot)
- Chat ID: 7880722190

## 📁 Estructura

```
monitoreomat/
├── monitor.py          # Script principal
├── .env               # Configuración (credenciales)
├── .env.example       # Ejemplo de configuración
├── requirements.txt   # Dependencias
└── README.md         # Esta documentación
```

## 🔧 Solución de problemas

### El token JWT no se obtiene
- Verifica que las credenciales en `.env` sean correctas
- El token expira, el script refresca automáticamente en cada verificación

### No llegan notificaciones
- Verifica que hayas iniciado una conversación con el bot en Telegram
- Confirma que el CHAT_ID sea correcto

### Error de conexión
- Verifica tu conexión a internet
- La página de la UNMSM puede estar en mantenimiento

## ⚠️ Notas

- Las credenciales están almacenadas localmente en `.env`
- El script hace login en cada verificación para evitar expiración de sesión
- Los trámites se consultan vía API REST (no scraping HTML)
