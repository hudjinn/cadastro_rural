#!/usr/bin/env python3
from flask import Flask, render_template, send_from_directory, jsonify, send_file
import os
import socket
import webbrowser
import threading
import time
import ssl
import subprocess
import zipfile
import io
from datetime import datetime, timedelta

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = 'cadastro-rural-2025'
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except socket.error:
        return "127.0.0.1"

def create_self_signed_cert():
    """Cria certificado auto-assinado para HTTPS"""
    cert_file = os.path.join(DIRECTORY, 'server.crt')
    key_file = os.path.join(DIRECTORY, 'server.key')
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    
    try:
        # Tentar usar openssl primeiro
        ip = get_ip_address()
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', key_file,
            '-out', cert_file, '-days', '365', '-nodes', '-subj', 
            f'/C=BR/ST=CE/L=Local/O=Dev/OU=Cadastro/CN={ip}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Certificado SSL criado com OpenSSL")
            return cert_file, key_file
        else:
            print(f"⚠️  OpenSSL falhou: {result.stderr}")
            
    except FileNotFoundError:
        print("⚠️  OpenSSL não encontrado, tentando com Python...")
    
    try:
        # Fallback: usar cryptography do Python
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        
        # Gerar chave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Criar certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CE"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cadastro Rural"),
            x509.NameAttribute(NameOID.COMMON_NAME, ip),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address(ip)),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Salvar certificado
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Salvar chave privada
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ Certificado SSL criado com Python cryptography")
        return cert_file, key_file
        
    except ImportError:
        print("❌ Biblioteca cryptography não encontrada")
        print("💡 Execute: pip install cryptography")
        return None, None
    except Exception as e:
        print(f"❌ Erro ao criar certificado: {e}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.webmanifest')
def manifest():
    return jsonify({
        "name": "Cadastro de Produtores Rurais",
        "short_name": "Cadastro Rural",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1976d2",
        "icons": [
            {
                "src": "/static/icon.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/icon.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    })
    
@app.route('/sw.js')
def service_worker():
    # garante o Content-Type correto e que está na raiz
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/download')
def download_zip():
    # Arquivos necessários
    files = [
        ('index.html', 'index.html'),
        ('manifest.webmanifest', 'manifest.webmanifest'),
        ('sw.js', 'sw.js'),
        ('static/css/bootstrap.min.css', 'static/css/bootstrap.min.css'),
        ('static/css/bootstrap-icons.css', 'static/css/bootstrap-icons.css'),
        ('static/js/bootstrap.bundle.min.js', 'static/js/bootstrap.bundle.min.js'),
        ('static/js/alpine.min.js', 'static/js/alpine.min.js'),
        ('static/js/jszip.min.js', 'static/js/jszip.min.js'),
        ('static/icon.png', 'static/icon.png'),
        # Adicione outros arquivos se necessário
    ]
    # Adiciona fontes dos ícones
    fonts = [
        ('static/fonts/bootstrap-icons.woff', 'static/fonts/bootstrap-icons.woff'),
        ('static/fonts/bootstrap-icons.woff2', 'static/fonts/bootstrap-icons.woff2'),
    ]
    files += fonts

    # Cria o ZIP em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for src, arcname in files:
            if os.path.exists(src):
                zip_file.write(src, arcname)
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='cadastro_rural_offline.zip')

def check_dependencies():
    """Verifica se as dependências locais existem"""
    required_files = [
        'static/css/bootstrap.min.css',
        'static/css/bootstrap-icons.css',
        'static/js/bootstrap.bundle.min.js',
        'static/js/alpine.min.js',
        'static/js/jszip.min.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def open_browser():
    time.sleep(2)
    # Tentar HTTPS primeiro, depois HTTP
    try:
        webbrowser.open('https://localhost:8443')
    except:
        webbrowser.open('http://localhost:8000')

@app.route('/instalar')
def instalar():
    return '''
    <html lang="pt-br">
    <head>
        <meta charset="utf-8">
        <title>Instalação Offline - Cadastro Rural</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: sans-serif; max-width: 500px; margin: 2rem auto; }
            .btn { display: inline-block; padding: 1rem 2rem; background: #1976d2; color: #fff; border-radius: 8px; text-decoration: none; font-size: 1.2rem; margin-top: 2rem;}
        </style>
    </head>
    <body>
        <h1>Instalação Offline</h1>
        <p>Para usar o sistema sem internet, baixe o pacote abaixo e extraia no seu dispositivo.</p>
        <a class="btn" href="/download">Baixar pacote offline (.zip)</a>
        <h2>Como usar:</h2>
        <ol>
            <li>Baixe e extraia o arquivo ZIP no seu celular/tablet.</li>
            <li>Abra o arquivo <b>index.html</b> usando o navegador.</li>
            <li>Adicione à tela inicial para instalar como aplicativo.</li>
        </ol>
        <p>Pronto! O sistema funcionará totalmente offline.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Verificar dependências
    missing_deps = check_dependencies()
    if missing_deps:
        print("\n⚠️  DEPENDÊNCIAS FALTANDO!")
        print("📁 Arquivos não encontrados:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Execute primeiro: python download_dependencies.py")
        print("🌐 (Requer internet para download inicial)")
        exit(1)
    
    # Criar diretórios se não existirem
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    ip = get_ip_address()
    
    # Tentar criar certificado SSL
    cert_file, key_file = create_self_signed_cert()
    
    print("\n" + "="*80)
    print("🌾 SISTEMA DE CADASTRO DE PRODUTORES RURAIS - FLASK")
    print("="*80)
    
    if cert_file and key_file:
        print("🔒 SERVIDOR HTTPS HABILITADO")
        print(f"🔐 HTTPS Local: https://localhost:8443")
        print(f"🌐 HTTPS Rede: https://{ip}:8443")
        print(f"🔓 HTTP Local: http://localhost:8000")
        print(f"🌍 HTTP Rede: http://{ip}:8000")
        print("="*80)
        print("✅ GPS funcionará perfeitamente via HTTPS!")
        print("⚠️  Aceite o certificado auto-assinado no navegador")
        print("📱 Para dispositivos móveis: use HTTPS")
        print("🔧 Pressione Ctrl+C para encerrar")
        print("="*80)
        
        # Abrir navegador automaticamente
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Iniciar servidores HTTPS e HTTP em paralelo
        def run_https():
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(cert_file, key_file)
                app.run(host='0.0.0.0', port=8443, ssl_context=context, debug=False, threaded=True)
            except Exception as e:
                print(f"❌ Erro no servidor HTTPS: {e}")
        
        def run_http():
            try:
                app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
            except Exception as e:
                print(f"❌ Erro no servidor HTTP: {e}")
        
        # Iniciar HTTPS em thread separada
        https_thread = threading.Thread(target=run_https, daemon=True)
        https_thread.start()
        
        # Aguardar um pouco antes de iniciar HTTP
        time.sleep(0.5)
        
        try:
            # Servidor HTTP principal
            run_http()
        except KeyboardInterrupt:
            print("\n🛑 Servidores Flask encerrados.")
    else:
        print("⚠️  APENAS HTTP DISPONÍVEL")
        print(f"🏠 Local: http://localhost:8000")
        print(f"🌐 Rede: http://{ip}:8000")
        print("="*80)
        print("⚠️  GPS só funcionará em localhost (sem HTTPS)")
        print("📱 Para GPS em dispositivos móveis, configure HTTPS")
        print("🔧 Pressione Ctrl+C para encerrar")
        print("="*80)
        
        # Abrir navegador automaticamente
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            app.run(host='0.0.0.0', port=8000, debug=False)
        except KeyboardInterrupt:
            print("\n🛑 Servidor Flask encerrado.")
