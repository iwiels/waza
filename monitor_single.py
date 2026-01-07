#!/usr/bin/env python3
"""
Monitor de Curso de Verano - UNMSM MAT
Versión para GitHub Actions (una sola ejecución)
"""

import os
import re
import json
import requests
from datetime import datetime

# ============ CONFIGURACIÓN ============
# Las credenciales vienen de variables de entorno (GitHub Secrets)
CONFIG = {
    "email": os.getenv("UNMSM_EMAIL", ""),
    "password": os.getenv("UNMSM_PASSWORD", ""),
    "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "local_code": os.getenv("LOCAL_CODE", "20"),  # 20 = FISI
}

URLS = {
    "login_page": "https://tramiteonline.unmsm.edu.pe/sgdfd/mat/login",
    "login_post": "https://tramiteonline.unmsm.edu.pe/sgdfd/mat/login",
    "tramites_page": "https://tramiteonline.unmsm.edu.pe/sgdfd/mat/tramites/solicitud",
    "api_tramites": "https://servicioonline.unmsm.edu.pe/sgdfd/mat/backend/tipos-tramite/local/{local}",
}

KEYWORDS = [
    "verano",
    "curso verano", 
    "curso de verano",
    "matricula verano",
    "matrícula verano",
    "ciclo verano",
]


class UNMSMMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.jwt_token = None
        self.codigo_alumno = None
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {msg}")

    def login(self):
        """Autenticarse en el sistema MAT"""
        self.log("🔐 Iniciando login...")
        
        resp = self.session.get(URLS["login_page"])
        csrf_match = re.search(r'name="_csrf" value="([^"]+)"', resp.text)
        if not csrf_match:
            self.log("❌ No se encontró token CSRF")
            return False
        csrf_token = csrf_match.group(1)
        
        email = CONFIG["email"]
        username = email.split("@")[0] if "@unmsm.edu.pe" in email else email
        
        data = {
            "_csrf": csrf_token,
            "login": username,
            "clave": CONFIG["password"]
        }
        
        resp = self.session.post(URLS["login_post"], data=data, allow_redirects=False)
        
        if resp.status_code != 302:
            self.log(f"❌ Login falló. Status: {resp.status_code}")
            return False
        
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            redirect_url = redirect_url.replace("http://", "https://")
            self.log(f"🔄 Siguiendo redirect...")
            self.session.get(redirect_url, allow_redirects=True)
            
        self.log("✅ Login exitoso")
        return True

    def get_jwt_token(self):
        """Obtener token JWT de la página de trámites"""
        self.log("🔑 Obteniendo token JWT...")
        
        resp = self.session.get(URLS["tramites_page"], allow_redirects=True)
        
        token_match = re.search(r'name="_t"\s+content="([^"]+)"', resp.text)
        if not token_match:
            token_match = re.search(r'name="_t" content="(eyJ[^"]+)"', resp.text)
        
        if not token_match or not token_match.group(1) or token_match.group(1).strip() == "":
            self.log("❌ No se encontró token JWT")
            if "login" in resp.url.lower():
                self.log("⚠️ Redirigido a login - sesión expirada")
            return False
        
        self.jwt_token = token_match.group(1)
        
        ca_match = re.search(r'name="_ca"\s+content="([^"]+)"', resp.text)
        if ca_match:
            self.codigo_alumno = ca_match.group(1)
        
        self.log(f"✅ Token obtenido. Código alumno: {self.codigo_alumno}")
        return True

    def get_tramites(self):
        """Obtener lista de trámites disponibles"""
        if not self.jwt_token:
            return None
            
        url = URLS["api_tramites"].format(local=CONFIG["local_code"])
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = self.session.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                self.log(f"❌ Error API: {resp.status_code}")
                return None
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return None

    def search_verano(self, tramites):
        """Buscar trámites relacionados con verano"""
        encontrados = []
        
        for tramite in tramites:
            nombre = tramite.get("nombre", "").lower()
            descripcion = tramite.get("descripcion", "").lower()
            asunto = tramite.get("asunto", "").lower()
            estado = tramite.get("nombreEstado", "")
            codigo_estado = tramite.get("codigoEstado", "")
            
            texto = f"{nombre} {descripcion} {asunto}"
            for keyword in KEYWORDS:
                if keyword in texto:
                    encontrados.append({
                        "nombre": tramite.get("nombre"),
                        "descripcion": tramite.get("descripcion"),
                        "estado": estado,
                        "codigo_estado": codigo_estado,
                        "disponible": codigo_estado == "1",
                        "url": tramite.get("nombreUrl"),
                    })
                    break
                    
        return encontrados

    def send_telegram(self, message):
        """Enviar mensaje por Telegram"""
        if not CONFIG["telegram_token"] or not CONFIG["telegram_chat_id"]:
            self.log("⚠️ Telegram no configurado")
            return False
            
        url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
        data = {
            "chat_id": CONFIG["telegram_chat_id"],
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            resp = requests.post(url, data=data)
            if resp.status_code == 200:
                self.log("✅ Notificación enviada por Telegram")
            return resp.status_code == 200
        except:
            return False

    def run(self):
        """Ejecutar una verificación"""
        self.log("=" * 50)
        self.log("🔍 MONITOR DE CURSO DE VERANO - UNMSM MAT")
        self.log("=" * 50)
        
        if not CONFIG["email"] or not CONFIG["password"]:
            self.log("❌ Faltan credenciales UNMSM (revisar secrets)")
            return False
        
        if not self.login():
            return False
            
        if not self.get_jwt_token():
            return False
            
        tramites = self.get_tramites()
        if not tramites:
            return False
            
        self.log(f"📋 Total trámites: {len(tramites)}")
        
        verano = self.search_verano(tramites)
        
        if verano:
            self.log(f"🎓 Trámites de verano encontrados: {len(verano)}")
            
            disponibles = []
            for t in verano:
                estado_emoji = "✅" if t["disponible"] else "❌"
                self.log(f"  {estado_emoji} {t['nombre']} - {t['estado']}")
                
                if t["disponible"]:
                    disponibles.append(t)
            
            # Si hay disponibles, notificar
            if disponibles:
                self.log("🎉 ¡TRÁMITE(S) DE VERANO DISPONIBLE(S)!")
                for t in disponibles:
                    message = f"""
🎓 <b>¡CURSO DE VERANO DISPONIBLE!</b> 🎓

📚 <b>Trámite:</b> {t['nombre']}
📝 <b>Descripción:</b> {t['descripcion']}
📊 <b>Estado:</b> {t['estado']}

🔗 <b>URL:</b>
https://tramiteonline.unmsm.edu.pe/sgdfd/mat/tipo-tramite/{t['url']}?local={CONFIG['local_code']}

⏰ <b>Detectado:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

¡Ingresa ahora para realizar tu matrícula!
"""
                    self.send_telegram(message.strip())
                return True
            else:
                self.log("⏳ Ningún trámite de verano disponible aún")
        else:
            self.log("❌ No se encontraron trámites de verano")
            
        return False


def main():
    monitor = UNMSMMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
