import streamlit as st
import yt_dlp
import os
import zipfile
import glob
import re

# ==========================================
# CONFIGURAÇÃO E FUNÇÕES AUXILIARES
# ==========================================

# Use um diretório de cache para evitar que o Streamlit remova os arquivos
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Função para sanitizar nomes de arquivos
def sanitize_filename(name):
    """Remove caracteres inválidos para nome de arquivo."""
    return re.sub(r'[\\/:*?"<>|]', '', name)

# Função para baixar vídeo
@st.cache_data(show_spinner=False)
def baixar_video(url, qualidade, pasta_destino=DOWNLOAD_DIR):
    """Baixa um vídeo do YouTube com a qualidade especificada."""
    try:
        ydl_opts = {
            'format': f'bestvideo[height<={qualidade[:-1]}]+bestaudio[ext=m4a]/best[ext=mp4]/best' if qualidade != 'best' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            file_name = ydl.prepare_filename(info).replace('.webm', '.mp4')
            st.info(f"Baixando **{info.get('title', '...')[:50]}**...")
            ydl.download([url])
        st.success("Download do vídeo concluído!")
        return file_name
    except Exception as e:
        st.error(f"Erro ao baixar o vídeo: {e}")
        return None

# Função para baixar áudio
@st.cache_data(show_spinner=False)
def baixar_audio(url, pasta_destino=DOWNLOAD_DIR):
    """Baixa apenas o áudio em MP3 de um vídeo do YouTube."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'verbose': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            file_name_mp3 = os.path.join(pasta_destino, f"{sanitize_filename(info.get('title'))}.mp3")
            st.info(f"Baixando **{info.get('title', '...')[:50]}** em MP3...")
            ydl.download([url])
        st.success("Download do áudio concluído!")
        return file_name_mp3
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {e}")
        return None

def listar_arquivos(pasta=DOWNLOAD_DIR):
    """Retorna uma lista de arquivos baixados."""
    return glob.glob(os.path.join(pasta, "*.*"))

def criar_zip(arquivos, nome_zip):
    """Cria um arquivo ZIP com os arquivos listados."""
    try:
        with zipfile.ZipFile(nome_zip, 'w') as zf:
            for file in arquivos:
                zf.write(file, os.path.basename(file))
        return nome_zip
    except Exception as e:
        st.error(f"Erro ao criar o ZIP: {e}")
        return None

# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 YouTube Downloader Interativo")
st.markdown("""
Esta é uma ferramenta simples para baixar vídeos e áudios do YouTube.
""")

with st.expander("ℹ️ Como usar"):
    st.markdown("""
    1.  Cole a URL do vídeo do YouTube no campo abaixo.
    2.  Escolha se deseja baixar o vídeo (MP4) ou apenas o áudio (MP3).
    3.  Clique em **Baixar**.
    4.  Após o download, você poderá reproduzir o arquivo ou criar um arquivo ZIP para baixar tudo de uma vez.
    """)

# --- Entrada de URL ---
url = st.text_input("🔗 URL do YouTube", help="Ex: https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if url:
    # --- Opções de Download ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Opções de Vídeo")
        qualidade_video = st.selectbox(
            "Qualidade do Vídeo",
            ("720p", "480p", "360p", "1080p", "best"),
            index=0,
            help="720p é o recomendado para um bom balanço entre qualidade e tamanho."
        )
        if st.button("⬇️ Baixar Vídeo"):
            with st.spinner("Baixando vídeo..."):
                caminho_video = baixar_video(url, qualidade_video)
                if caminho_video:
                    st.video(caminho_video)

    with col2:
        st.subheader("Opções de Áudio")
        st.markdown("_(MP3 de alta qualidade)_")
        if st.button("🎶 Baixar Áudio"):
            with st.spinner("Baixando áudio..."):
                caminho_audio = baixar_audio(url)
                if caminho_audio:
                    st.audio(caminho_audio)
else:
    st.info("👆 Por favor, insira uma URL para começar.")

# --- Gerenciar downloads ---
st.markdown("---")
st.header("📂 Downloads Concluídos")
arquivos_baixados = listar_arquivos()

if not arquivos_baixados:
    st.info("Nenhum arquivo baixado ainda.")
else:
    # Exibir a lista de arquivos
    df_files = st.dataframe(
        [
            {"nome": os.path.basename(f), "tamanho (MB)": f"{os.path.getsize(f) / (1024 * 1024):.2f}"}
            for f in arquivos_baixados
        ],
        hide_index=True,
    )
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📦 Criar ZIP de todos os arquivos"):
            zip_filename = "downloads.zip"
            with st.spinner("Criando arquivo ZIP..."):
                caminho_zip = criar_zip(arquivos_baixados, zip_filename)
                if caminho_zip:
                    st.success(f"Arquivo ZIP criado: `{zip_filename}`")
                    st.download_button(
                        label="Clique para baixar o ZIP",
                        data=open(caminho_zip, 'rb').read(),
                        file_name=zip_filename,
                        mime='application/zip',
                    )

    with col4:
        if st.button("🗑️ Limpar pasta de downloads"):
            for file in arquivos_baixados:
                os.remove(file)
            st.success("Pasta de downloads limpa!")
            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center;'>Criado com Streamlit, yt-dlp e ffmpeg</p>", unsafe_allow_html=True)
