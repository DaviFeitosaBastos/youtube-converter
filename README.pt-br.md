# Youtube Conversor

Uma ferramenta CLI em Python para baixar vídeos e áudios do YouTube, além de converter arquivos MP4 para GIF diretamente pelo terminal, com uma interface de menu limpa e interativa usando Rich.

---

## Funcionalidades

- Baixar vídeos do YouTube em **alta ou baixa resolução**
- Baixar **faixas de áudio** do YouTube como MP3
- Converter **vídeos MP4 para GIF** com configurações personalizáveis (FPS, resolução, corte)
- Visualizar **metadados do vídeo** antes de baixar
- Menu interativo com validação de URL
- Interface de terminal limpa usando Rich

---

## Estrutura do Projeto

```
Youtube_conversor/
├── main.py               # Ponto de entrada da aplicação
├── router.py             # Roteamento e lógica de navegação do menu
├── .gitignore            # Ignora arquivos desnecessários
├── README.md             # Versão em inglês
├── README.pt-BR.md       # Você está lendo agora
├── requirements.txt      # Todas as dependências
├── __init__.py
├── gifs/
│   └── # GIFs convertidos ficam aqui
├── web/
│   ├── __init__.py
│   └── log_utils.py     # Utilitários compartilhados (get_base_dir)(logger)
├── service/
│   ├── video_service.py  # Lógica de download de vídeo (alta res, baixa res, info)
│   ├── track_service.py  # Lógica de download de áudio
│   └── gif_service.py    # Lógica de conversão MP4 para GIF
└── ui/
    ├── __init__.py
    ├── display.py        # Helpers de exibição CLI (cabeçalhos, menus, carregamento)
    └── validation.py     # Validação de entrada (URL, inteiros, sim/não, seletor de arquivo)
```

---

## Configuração do Ambiente

**Crie e ative um ambiente virtual:**

```bash
python -m venv venv

# Linux
source venv/bin/activate

# Windows
venv\Scripts\Activate
```

**Instale as dependências:**

```bash
pip install -r requirements.txt
```

> Certifique-se de que o `ffmpeg` está instalado no seu sistema e disponível no PATH.
>
> Linux: `sudo apt install ffmpeg`
>
> Windows: https://ffmpeg.org/download.html

---

## Uso

```bash
# linux
python3 main.py

# windows
python main.py
```

Navegue usando as opções numeradas:

```
================================
         Menu principal
================================
1 - Baixar vídeos do [YOUTUBE]
2 - Baixar faixa de áudio do [YOUTUBE]
3 - Converter MP4 para GIF
0 - Sair
```

Após selecionar uma opção, siga as instruções no terminal.

---


A interface de terminal usa painéis Rich, menus numerados, status do FFmpeg e indicação da pasta de saída. Use os números para navegar, Enter para continuar e Ctrl+C para sair.

## Pastas de Saída

As pastas são criadas quando necessárias no diretório de dados do usuário (veja abaixo):

| Pasta | Conteúdo |
|---|---|
| `videos/` | Vídeos MP4 baixados |
| `audios/` | Faixas MP3 baixadas |
| `gifs/` | Arquivos GIF convertidos |

---

## Gerando o Executável

```bash
python -m pip install -r requirements-build.txt
python -m PyInstaller --onefile --paths . --name Youtube_conversor main.py
```

> O executável fica em `dist/`. O FFmpeg continua sendo um requisito externo, disponível no PATH.

---

## Dependências

| Pacote | Finalidade |
|---|---|
| `pytubefix` | Download de vídeo/áudio do YouTube |
| `ffmpeg-python` | Conversão de MP4 para GIF |
| `rich` | Estilização da interface no terminal |

---

## Roadmap

- [ ] Versão web da aplicação
- [ ] Interface gráfica no lugar do terminal
- [ ] Suporte a múltiplos provedores além do YouTube

---

## Notas

- Esta ferramenta é destinada apenas para uso pessoal.
- Respeite os Termos de Serviço do YouTube ao baixar conteúdo.

---

## Transparência sobre o uso de IA

O OpenAI Codex auxiliou na revisão deste projeto, correção de bugs, criação de
testes automatizados, configuração do CI e documentação. Essa assistência não
significa que o projeto original tenha sido inteiramente gerado por IA.

A IA é usada como assistente de desenvolvimento. O aplicativo não chama APIs de
IA generativa nem envia URLs ou mídias do usuário a um serviço de IA durante a
execução normal. Downloads do YouTube continuam exigindo requisições de rede,
conforme descrito em [PRIVACY.md](PRIVACY.md).

---

## Autor

[DaviFeitosaBastos](https://github.com/DaviFeitosaBastos)

## Linux e Windows, testes e privacidade

Requer Python 3.11 ou superior e FFmpeg no PATH. No Windows, use
`venv\Scripts\Activate.ps1` no PowerShell ou `venv\Scripts\activate.bat` no CMD.

As mídias ficam em `~/.local/share/youtube-converter` (Linux; respeita
`XDG_DATA_HOME`) ou `%LOCALAPPDATA%\youtube-converter` (Windows).
Para manter a pasta de saída antiga, configure `YOUTUBE_CONVERTER_DATA_DIR`
com o caminho absoluto do projeto. Os arquivos antigos não são movidos ou apagados.
O conversor aceita um caminho MP4 externo ou a seleção entre os downloads.

```bash
python main.py --check
python -m unittest discover -s tests -v
```

O CI testa Linux e Windows, Python 3.11 e 3.14. Tags `v*` geram executáveis
separados por sistema e publicam uma release; execução manual gera artefatos.
Não há backend web nesta versão.

Leia [PRIVACY.md](PRIVACY.md) para dados usados, terceiros, retenção e exclusão.
Não há telemetria nem logs persistentes. Isso não constitui certificação jurídica
de conformidade com a LGPD.

No Linux, o executável baixado pode precisar de `chmod +x Youtube_conversor-Linux`.
O build usa o ambiente Ubuntu do CI; distribuições antigas podem exigir compilação local.
