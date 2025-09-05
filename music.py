import streamlit as st
import json
import os
import requests
from datetime import datetime, timedelta
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tempfile
import subprocess

class CookieManager:
    def __init__(self):
        self.cookies_file = "music_cookies.json"
        self.session = requests.Session()
    
    def save_cookies(self, cookies, service_name):
        """Salva cookies para um serviço específico"""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                all_cookies = json.load(f)
        else:
            all_cookies = {}
        
        all_cookies[service_name] = {
            'cookies': cookies,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.cookies_file, 'w') as f:
            json.dump(all_cookies, f, indent=2)
    
    def load_cookies(self, service_name):
        """Carrega cookies de um serviço específico"""
        if not os.path.exists(self.cookies_file):
            return None
        
        with open(self.cookies_file, 'r') as f:
            all_cookies = json.load(f)
        
        if service_name in all_cookies:
            cookie_data = all_cookies[service_name]
            # Verifica se os cookies não estão muito antigos (30 dias)
            timestamp = datetime.fromisoformat(cookie_data['timestamp'])
            if datetime.now() - timestamp < timedelta(days=30):
                return cookie_data['cookies']
        
        return None
    
    def extract_cookies_selenium(self, service_url, service_name):
        """Extrai cookies usando Selenium"""
        try:
            options = Options()
            options.add_argument('--headless=False')  # Mostra o navegador para login
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(service_url)
            
            st.info(f"Navegador aberto para {service_name}. Faça login e pressione Enter aqui quando terminar.")
            
            # Aguarda o usuário fazer login
            user_input = st.text_input("Pressione Enter após fazer login no navegador:", key=f"login_{service_name}")
            
            if user_input is not None:
                cookies = driver.get_cookies()
                self.save_cookies(cookies, service_name)
                driver.quit()
                st.success(f"Cookies salvos para {service_name}!")
                return cookies
            
        except Exception as e:
            st.error(f"Erro ao extrair cookies: {str(e)}")
            return None
    
    def import_browser_cookies(self, service_name, browser='chrome'):
        """Importa cookies diretamente do navegador"""
        try:
            # Para YouTube, usa yt-dlp para extrair cookies
            if service_name.lower() in ['youtube', 'youtube music']:
                cookies_file = f"cookies_{service_name.lower().replace(' ', '_')}.txt"
                
                # Comando para extrair cookies do navegador
                cmd = f"yt-dlp --cookies-from-browser {browser} --cookies {cookies_file} --skip-download 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if os.path.exists(cookies_file):
                    st.success(f"Cookies do {browser} importados com sucesso!")
                    return cookies_file
                else:
                    st.error("Falha ao importar cookies do navegador")
                    
        except Exception as e:
            st.error(f"Erro ao importar cookies: {str(e)}")
        
        return None

class MusicPlayer:
    def __init__(self):
        self.cookie_manager = CookieManager()
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extract_flat': False,
        }
    
    def setup_youtube_cookies(self):
        """Configura cookies para YouTube"""
        cookies = self.cookie_manager.load_cookies('youtube')
        if cookies:
            # Converte cookies para formato yt-dlp
            cookies_file = "youtube_cookies.txt"
            self.convert_cookies_to_netscape(cookies, cookies_file)
            self.ydl_opts['cookiefile'] = cookies_file
            return True
        return False
    
    def convert_cookies_to_netscape(self, cookies, filename):
        """Converte cookies JSON para formato Netscape"""
        with open(filename, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                expiration = cookie.get('expiry', 0)
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
    
    def search_music(self, query, max_results=5):
        """Pesquisa música no YouTube"""
        try:
            search_opts = self.ydl_opts.copy()
            search_opts.update({
                'quiet': True,
                'extract_flat': True,
                'default_search': 'ytsearch' + str(max_results) + ':'
            })
            
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                search_results = ydl.extract_info(query, download=False)
                
                results = []
                if 'entries' in search_results:
                    for entry in search_results['entries']:
                        results.append({
                            'title': entry.get('title', 'Título não disponível'),
                            'id': entry.get('id', ''),
                            'url': entry.get('url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Desconhecido')
                        })
                
                return results
                
        except Exception as e:
            st.error(f"Erro na pesquisa: {str(e)}")
            return []
    
    def get_audio_info(self, video_url):
        """Obtém informações de áudio do vídeo"""
        try:
            info_opts = self.ydl_opts.copy()
            info_opts['quiet'] = True
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                audio_url = None
                for format in info.get('formats', []):
                    if format.get('acodec') != 'none' and format.get('vcodec') == 'none':
                        audio_url = format['url']
                        break
                
                return {
                    'title': info.get('title', ''),
                    'audio_url': audio_url,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', '')
                }
                
        except Exception as e:
            st.error(f"Erro ao obter informações do áudio: {str(e)}")
            return None

def main():
    st.set_page_config(page_title="🎵 Music Player", layout="wide")
    
    st.title("🎵 Sistema de Reprodução de Música")
    st.markdown("---")
    
    # Inicializa o player
    if 'player' not in st.session_state:
        st.session_state.player = MusicPlayer()
    
    # Sidebar para gerenciamento de cookies
    with st.sidebar:
        st.header("🍪 Gerenciamento de Cookies")
        
        service_options = ['YouTube', 'YouTube Music', 'Spotify', 'Outro']
        selected_service = st.selectbox("Selecionar Serviço:", service_options)
        
        st.subheader("Opções de Cookies:")
        
        # Botão para importar cookies do navegador
        if st.button("📥 Importar do Navegador"):
            browser = st.selectbox("Navegador:", ['chrome', 'firefox', 'edge'])
            result = st.session_state.player.cookie_manager.import_browser_cookies(selected_service, browser)
            if result:
                st.success("Cookies importados!")
        
        # Upload manual de arquivo de cookies
        st.subheader("📁 Upload Manual")
        uploaded_file = st.file_uploader("Upload arquivo de cookies (.json ou .txt)", type=['json', 'txt'])
        
        if uploaded_file:
            if uploaded_file.name.endswith('.json'):
                cookies_data = json.load(uploaded_file)
                st.session_state.player.cookie_manager.save_cookies(cookies_data, selected_service)
                st.success("Cookies JSON carregados!")
            elif uploaded_file.name.endswith('.txt'):
                # Salva arquivo de cookies Netscape
                with open(f"cookies_{selected_service.lower()}.txt", "wb") as f:
                    f.write(uploaded_file.read())
                st.success("Cookies Netscape carregados!")
        
        # Status dos cookies
        st.subheader("📊 Status dos Cookies")
        cookies = st.session_state.player.cookie_manager.load_cookies(selected_service)
        if cookies:
            st.success(f"✅ Cookies ativos para {selected_service}")
        else:
            st.warning(f"❌ Sem cookies para {selected_service}")
    
    # Interface principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Pesquisar Música")
        search_query = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Imagine Dragons - Believer")
        
        if st.button("🔎 Pesquisar"):
            if search_query:
                with st.spinner("Pesquisando..."):
                    # Configura cookies para YouTube se disponível
                    st.session_state.player.setup_youtube_cookies()
                    
                    results = st.session_state.player.search_music(search_query)
                    st.session_state.search_results = results
            else:
                st.warning("Digite algo para pesquisar!")
        
        # Exibe resultados da pesquisa
        if 'search_results' in st.session_state and st.session_state.search_results:
            st.subheader("📋 Resultados da Pesquisa:")
            
            for i, result in enumerate(st.session_state.search_results):
                with st.expander(f"🎵 {result['title'][:50]}..."):
                    col_info, col_play = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**Artista:** {result['uploader']}")
                        if result['duration']:
                            minutes = result['duration'] // 60
                            seconds = result['duration'] % 60
                            st.write(f"**Duração:** {minutes}:{seconds:02d}")
                    
                    with col_play:
                        if st.button("▶️ Reproduzir", key=f"play_{i}"):
                            video_url = f"https://www.youtube.com/watch?v={result['id']}"
                            
                            with st.spinner("Carregando áudio..."):
                                audio_info = st.session_state.player.get_audio_info(video_url)
                                
                                if audio_info and audio_info['audio_url']:
                                    st.session_state.current_song = audio_info
                                    st.success("✅ Música carregada!")
                                else:
                                    st.error("❌ Erro ao carregar música")
    
    with col2:
        st.header("🎵 Player Atual")
        
        if 'current_song' in st.session_state:
            song = st.session_state.current_song
            
            if song['thumbnail']:
                st.image(song['thumbnail'], caption=song['title'])
            
            st.write(f"**🎵 Tocando:** {song['title']}")
            
            if song['duration']:
                minutes = song['duration'] // 60
                seconds = song['duration'] % 60
                st.write(f"**⏱️ Duração:** {minutes}:{seconds:02d}")
            
            # Player de áudio HTML5
            if song['audio_url']:
                st.markdown(f"""
                <audio controls style="width: 100%">
                    <source src="{song['audio_url']}" type="audio/mpeg">
                    Seu navegador não suporta o elemento de áudio.
                </audio>
                """, unsafe_allow_html=True)
        else:
            st.info("🎵 Nenhuma música selecionada")
            st.markdown("Pesquise e selecione uma música para começar!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>🎵 Music Player com Sistema de Cookies 🍪</p>
        <p><small>Desenvolvido com Streamlit e yt-dlp</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
