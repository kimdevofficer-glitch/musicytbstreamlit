# requirements.txt
streamlit>=1.28.0
yt-dlp>=2023.10.13
requests>=2.31.0
selenium>=4.15.0
webdriver-manager>=4.0.1

# setup_instructions.md

# 🎵 Sistema de Música com Cookies - Guia de Instalação

## 📋 Pré-requisitos

1. **Python 3.8+** instalado
2. **Chrome** ou **Firefox** instalado
3. **ChromeDriver** (será instalado automaticamente)

## 🚀 Instalação Rápida

### 1. Clone ou baixe os arquivos

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Instale dependências adicionais
```bash
# Para Windows
pip install webdriver-manager

# Para Linux/Mac (pode precisar de ffmpeg)
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg         # macOS
```

## 🍪 Configuração de Cookies

### Método 1: Importação Automática do Navegador
1. Faça login no YouTube/serviço no seu navegador
2. Use o botão "Importar do Navegador" no app
3. Selecione seu navegador (Chrome recomendado)

### Método 2: Upload Manual
1. Use extensão "Get cookies.txt LOCALLY" no Chrome
2. Exporte cookies do YouTube
3. Faça upload do arquivo no app

### Método 3: Extração com Selenium
1. Use o botão para abrir navegador automático
2. Faça login manualmente
3. Cookies serão salvos automaticamente

## ▶️ Executar o App

```bash
streamlit run music_player.py
```

## 🔧 Solução de Problemas

### Erro de ChromeDriver
```bash
pip install --upgrade webdriver-manager
```

### Erro de yt-dlp
```bash
pip install --upgrade yt-dlp
```

### Problemas de áudio
- Instale ffmpeg no sistema
- Verifique se as URLs de áudio não expiraram

### Cookies expirados
- Re-importe cookies do navegador
- Verifique se está logado no serviço

## 📁 Estrutura de Arquivos

```
music_player/
├── music_player.py          # Arquivo principal
├── requirements.txt         # Dependências
├── music_cookies.json       # Cookies salvos (gerado automaticamente)
├── cookies_youtube.txt      # Cookies Netscape (opcional)
└── setup_instructions.md    # Este arquivo
```

## ⚠️ Avisos Importantes

1. **Cookies são sensíveis** - não compartilhe arquivos de cookies
2. **Terms of Service** - use responsavelmente
3. **Rate Limiting** - não abuse das APIs
4. **Backup** - salve seus cookies importantes

## 🎵 Recursos Disponíveis

- ✅ Pesquisa no YouTube
- ✅ Reprodução de áudio
- ✅ Gerenciamento de cookies
- ✅ Interface amigável
- ✅ Suporte a múltiplos serviços
- ✅ Importação automática de cookies
- ✅ Player HTML5 integrado

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o navegador está atualizado
3. Teste com cookies novos
4. Verifique a conexão com internet
