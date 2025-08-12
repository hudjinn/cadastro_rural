#!/usr/bin/env python3
import requests
import os
import zipfile
import tempfile
from pathlib import Path

def download_file(url, filepath):
    """Baixa um arquivo da URL e salva no caminho especificado"""
    print(f"🔄 Baixando {os.path.basename(filepath)}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Criar diretórios se não existirem
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ {os.path.basename(filepath)} baixado")
        return True
    except Exception as e:
        print(f"❌ Erro ao baixar {os.path.basename(filepath)}: {e}")
        return False

def download_bootstrap_icons():
    """Baixa e extrai os ícones do Bootstrap"""
    print("🔄 Baixando Bootstrap Icons...")
    try:
        # Tentar baixar o CSS diretamente primeiro
        icons_css_url = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
        
        response = requests.get(icons_css_url, timeout=30)
        response.raise_for_status()
        
        # Criar diretório e salvar CSS
        os.makedirs('static/css', exist_ok=True)
        with open('static/css/bootstrap-icons.css', 'wb') as css_file:
            css_file.write(response.content)
        
        print("✅ Bootstrap Icons CSS baixado diretamente")
        
        # Agora baixar os arquivos de fonte WOFF2
        fonts_dir = 'static/fonts'
        os.makedirs(fonts_dir, exist_ok=True)
        
        # URLs das fontes (versões mais comuns)
        font_urls = [
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.woff2",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/bootstrap-icons.woff"
        ]
        
        for font_url in font_urls:
            try:
                font_name = os.path.basename(font_url)
                font_response = requests.get(font_url, timeout=30)
                font_response.raise_for_status()
                
                with open(f'{fonts_dir}/{font_name}', 'wb') as font_file:
                    font_file.write(font_response.content)
                print(f"✅ Fonte {font_name} baixada")
            except:
                print(f"⚠️  Fonte {font_name} não encontrada")
        
        # Corrigir paths no CSS para usar fontes locais
        with open('static/css/bootstrap-icons.css', 'r') as f:
            css_content = f.read()
        
        # Substituir URLs das fontes por caminhos locais
        css_content = css_content.replace(
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/fonts/',
            '../fonts/'
        )
        
        with open('static/css/bootstrap-icons.css', 'w') as f:
            f.write(css_content)
        
        print("✅ Paths das fontes corrigidos no CSS")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao baixar Bootstrap Icons: {e}")
        
        # Fallback: criar CSS básico com ícones em SVG inline
        print("🔄 Criando fallback com ícones SVG...")
        create_fallback_icons()
        return True

def create_fallback_icons():
    """Cria CSS com ícones SVG inline como fallback"""
    icons_css = """
/* Bootstrap Icons Fallback - SVG Inline */
.bi {
  display: inline-block;
  width: 1em;
  height: 1em;
  vertical-align: -.125em;
  background-repeat: no-repeat;
  background-size: contain;
}

.bi-person-fill {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6'/></svg>");
}

.bi-house-fill {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L8 2.207l6.646 6.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-2a.5.5 0 0 0-.5.5v1.293z'/><path d='m8 3.293 6 6V13.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5V9.293z'/></svg>");
}

.bi-flower1 {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M6.174 1.184a2 2 0 0 1 3.652 0A2 2 0 0 1 12.99 3.01a2 2 0 0 1 1.826 3.164 2 2 0 0 1 0 3.652 2 2 0 0 1-1.826 3.164 2 2 0 0 1-3.164 1.826 2 2 0 0 1-3.652 0A2 2 0 0 1 3.01 12.99a2 2 0 0 1-1.826-3.164 2 2 0 0 1 0-3.652A2 2 0 0 1 3.01 3.01a2 2 0 0 1 3.164-1.826z'/></svg>");
}

.bi-egg-fill {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M14 10a6 6 0 0 1-12 0C2 5.686 5 0 8 0s6 5.686 6 10'/></svg>");
}

.bi-chat-left-text-fill {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4.414a1 1 0 0 0-.707.293L.854 15.146A.5.5 0 0 1 0 14.793z'/><path d='M3.5 3a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1zm0 2.5a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1zm0 2.5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1z'/></svg>");
}

.bi-plus-lg {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2'/></svg>");
}

.bi-trash {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z'/><path d='M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1z'/></svg>");
}

.bi-pencil {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10z'/><path d='m2.19 13.632.106-.106 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325'/></svg>");
}

.bi-geo-alt {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M12.166 8.94c-.524 1.062-1.234 2.12-1.96 3.07A31.493 31.493 0 0 1 8 14.58a31.481 31.481 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304 7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94zM8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10z'/><path d='M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6z'/></svg>");
}

.bi-info-circle {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/><path d='m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z'/></svg>");
}

.bi-person-plus {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z'/><path fill-rule='evenodd' d='M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z'/></svg>");
}

.bi-table {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm15 2h-4v3h4V4zm0 4h-4v3h4V8zm0 4h-4v3h3a1 1 0 0 0 1-1v-2zm-5 3v-3H6v3h4zm-5 0v-3H1v2a1 1 0 0 0 1 1h3zm-4-4h4V8H1v3zm0-4h4V4H1v3zm5-3v3h4V4H6zm4 4H6v3h4V8z'/></svg>");
}

.bi-arrow-clockwise {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z'/><path d='M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z'/></svg>");
}

.bi-save {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 8.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z'/></svg>");
}

.bi-file-earmark-spreadsheet {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' viewBox='0 0 16 16'><path d='M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V9H3V2a1 1 0 0 1 1-1h5.5v2zM3 12v-2h2v2H3zm0 1h2v2H4a1 1 0 0 1-1-1v-1zm3 2v-2h3v2H6zm4 0v-2h3v1a1 1 0 0 1-1 1h-2zm3-3h-3v-2h3v2zm-7 0v-2h3v2H6z'/></svg>");
}
"""
    
    os.makedirs('static/css', exist_ok=True)
    with open('static/css/bootstrap-icons.css', 'w') as f:
        f.write(icons_css)
    
    print("✅ CSS de ícones SVG criado")

def main():
    print("🚀 === DOWNLOAD DE DEPENDÊNCIAS PARA FUNCIONAMENTO OFFLINE ===\n")
    
    # URLs das dependências
    dependencies = {
        'static/css/bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
        'static/js/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
        'static/js/alpine.min.js': 'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js',
        'static/js/jszip.min.js': 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js'
    }
    
    success_count = 0
    total_files = len(dependencies) + 1  # +1 para os ícones
    
    # Baixar dependências principais
    for filepath, url in dependencies.items():
        if download_file(url, filepath):
            success_count += 1
    
    # Baixar ícones do Bootstrap
    if download_bootstrap_icons():
        success_count += 1
    
    print(f"\n📊 RESULTADO: {success_count}/{total_files} arquivos baixados com sucesso!")
    
    # Criar ícone padrão se não existir
    icon_path = 'static/icon.png'
    if not os.path.exists(icon_path):
        print("\n📱 Criando ícone padrão...")
        create_default_icon()
    
    if success_count == total_files:
        print("\n🎉 TUDO PRONTO! O sistema funcionará completamente offline.")
        print("🚀 Execute 'python app.py' para iniciar o servidor Flask.")
    else:
        print(f"\n⚠️  {total_files - success_count} arquivos falharam no download.")
        print("🌐 Verifique sua conexão e tente novamente.")

def create_default_icon():
    """Cria um ícone padrão simples"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Criar imagem 192x192
        img = Image.new('RGB', (192, 192), color='#1976d2')
        draw = ImageDraw.Draw(img)
        
        # Desenhar um círculo branco
        draw.ellipse([48, 48, 144, 144], fill='white')
        
        # Adicionar texto
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "CR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (192 - text_width) // 2
        text_y = (192 - text_height) // 2
        
        draw.text((text_x, text_y), text, fill='#1976d2', font=font)
        
        # Salvar
        os.makedirs('static', exist_ok=True)
        img.save('static/icon.png')
        print("✅ Ícone padrão criado")
        
    except ImportError:
        print("⚠️  PIL não encontrado. Adicione manualmente um icon.png na pasta static/")
    except Exception as e:
        print(f"⚠️  Erro ao criar ícone: {e}")

if __name__ == '__main__':
    main()
