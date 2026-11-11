# YouTube Converter

Aplicativo desktop para Linux e Windows, com interface em português feita em
HTML/CSS/JavaScript e uma janela nativa usando **pywebview**. Baixe vídeos MP4,
extraia MP3 e transforme arquivos MP4 em GIF sem usar um terminal no dia a dia.

## O que funciona

- Vídeos do YouTube em alta qualidade ou menor resolução.
- Extração de áudio em MP3 e consulta de informações do vídeo.
- Conversão local de MP4 para GIF com corte, FPS e largura configuráveis.
- Seletores nativos de arquivos e da pasta de saída.
- Progresso da etapa atual, cancelamento e mensagens de erro na janela.
- Uma operação por vez, sem sobrescrever arquivos existentes.
- Interface de terminal preservada como alternativa em `main.py`.

A pasta `web/` contém a interface real do aplicativo. Abrir `index.html` no
navegador permite visualizar o layout, mas as operações exigem a janela desktop.
Não há API HTTP nem servidor de aplicação; a comunicação usa a ponte do pywebview.

## Abrir sem terminal

Nos artefatos do GitHub Actions ou em uma release, baixe o ZIP do seu sistema e
**extraia a pasta inteira**. Mantenha a pasta `_internal` junto do executável.

- **Windows:** abra `YouTube-Converter-Windows.exe` com dois cliques. O aplicativo
  usa Microsoft Edge WebView2 Runtime, que precisa estar instalado.
- **Linux:** abra `YouTube-Converter-Linux` pelo gerenciador de arquivos. Se
  necessário, permita executar o arquivo nas propriedades. O pacote inclui Qt,
  mas depende das bibliotecas gráficas usuais do sistema. O build do CI usa Ubuntu
  24.04; outras distribuições podem exigir um build local.

O **FFmpeg precisa estar instalado e disponível no PATH**. Ele não é incluído no
ZIP. A janela informa quando ele está ausente. Python não é necessário nos pacotes.

## Executar a partir do código

A instalação inicial requer Python 3.11 ou superior e comandos no terminal.
Depois, use o atalho para abrir a janela.

```bash
python -m venv venv
```

Linux:

```bash
./venv/bin/python -m pip install -r requirements-desktop.txt
./venv/bin/python scripts/create_shortcut.py
```

Abra o arquivo gerado **YouTube Converter.desktop**. Dependendo do ambiente,
marque-o como executável/confiável no gerenciador de arquivos. Ele aponta para
esta cópia do projeto; gere-o novamente se mover a pasta.

Windows (PowerShell):

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
```

Depois, abra **Start-Windows.vbs** com dois cliques. Ele usa o Python do ambiente
virtual sem abrir console e requer o Windows Script Host habilitado.
Também é possível criar um atalho para `venv\Scripts\pythonw.exe desktop.py`,
com a pasta do projeto como diretório de trabalho.

Para iniciar a janela diretamente durante o desenvolvimento:

```bash
python desktop.py
```

Use o Python do ambiente virtual. No Linux, as dependências desktop usam
PySide6/QtWebEngine. No Windows, usam o renderizador Edge Chromium.
Consulte a [instalação oficial do pywebview](https://pywebview.flowrl.com/guide/installation)
para os requisitos gráficos do sistema e o [FFmpeg](https://ffmpeg.org/download.html)
para instalar o conversor.

## Como usar

1. Em **YouTube**, cole o link, escolha MP4 ou MP3 e clique em baixar.
2. Em **MP4 para GIF**, escolha um arquivo pelo seletor, informe início/fim em
   `HH:MM:SS`, ajuste FPS/largura e clique em criar.
3. Use **Alterar** no rodapé para escolher a pasta e **Abrir pasta** para ver os
   arquivos. A escolha da pasta vale apenas para a sessão atual.

O progresso é por etapa; a barra pode reiniciar ao começar outra faixa. Durante
junção/conversão, é exibido progresso indeterminado. Cancelar pode aguardar a
requisição de rede ou etapa atual. Fechar a janela durante uma operação solicita
cancelamento; aguarde a conclusão e feche novamente.

Pastas padrão: `~/.local/share/youtube-converter` no Linux (respeita `XDG_DATA_HOME`)
e `%LOCALAPPDATA%\youtube-converter` no Windows. `YOUTUBE_CONVERTER_DATA_DIR`
permite configurar outra pasta. Resultados ficam em `videos/`, `audios/` e `gifs/`.
Arquivos de versões anteriores não são movidos ou apagados.

## Terminal opcional

```bash
python -m pip install -r requirements.txt
python main.py --check
python main.py
```

## Testes e empacotamento

```bash
python -m tests
python desktop.py --check
python -m tests.desktop_smoke
python -m pip install -r requirements-build.txt
python scripts/build_desktop.py
```

O teste gráfico requer um ambiente desktop e FFmpeg; usa vídeo sintético, sem
acessar o YouTube ou arquivos pessoais. Em Linux sem tela, pode usar Qt offscreen
com renderização por software. Não desative o sandbox do Chromium.

O build produz `dist/YouTube-Converter-Linux.zip` ou
`dist/YouTube-Converter-Windows.zip`, conforme o sistema de compilação. O CI testa
Python 3.11/3.14 em Linux e Windows e gera pacotes em pushes para `main` ou por
execução manual. Tags `v*` também publicam uma release após os testes e builds.

## Privacidade e uso de IA

Sem telemetria, conta, histórico persistente ou logs de URLs. A janela usa recursos
locais e perfil privado. Downloads consultam servidores do YouTube/Google;
conversões de MP4 para GIF são locais. Veja [PRIVACY.md](PRIVACY.md) para os dados
usados, terceiros, retenção, exclusão e limites da adequação à LGPD.

OpenAI Codex auxiliou na revisão, correções, testes, interface desktop, CI e
documentação. Isso não significa que o projeto original foi inteiramente gerado
por IA. O aplicativo não chama APIs de IA generativa nem envia URLs ou mídias a
serviços de IA durante a execução normal.

Baixe apenas conteúdo que você tenha autorização para utilizar. Respeite os
termos dos serviços e os direitos das pessoas presentes nas mídias.

## Estrutura

- `desktop.py`: abertura da janela e carregamento dos recursos locais.
- `web/`: interface desktop em HTML, CSS e JavaScript.
- `ui/desktop_api.py`: ponte da janela, seletores e operações em segundo plano.
- `service/media_engine.py`: operações compartilhadas entre desktop e CLI.
- `main.py`, `router.py`, `ui/display.py`: alternativa de terminal.
- `scripts/`: geração de atalho Linux e empacotamento.
- `tests/`: regressões, ponte desktop e teste da janela com FFmpeg real.

## Autor

[Davi Feitosa Bastos](https://github.com/DaviFeitosaBastos)
