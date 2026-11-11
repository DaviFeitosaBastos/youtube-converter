# Privacidade e proteção de dados

O aplicativo é executado localmente, sem cadastro, servidor próprio, telemetria,
analytics ou histórico persistente de URLs. A interface em `web/` é carregada em
uma janela pywebview com recursos locais e perfil privado. Ela se comunica com
Python por uma ponte no próprio processo, sem API HTTP ou servidor de aplicação.
URLs, arquivos selecionados, pasta de saída e atividade ficam em memória durante
a sessão. A pasta escolhida na janela não é persistida entre sessões. O renderizador
pode usar arquivos temporários e caches técnicos; perfil privado não é uma garantia
de apagamento seguro do armazenamento do sistema.

## Dados e finalidade

- A URL informada é usada para consultar metadados e baixar a mídia solicitada.
  O YouTube/Google e seus servidores de distribuição recebem as requisições
  necessárias, incluindo o endereço IP e dados técnicos da conexão. Esses
  serviços podem processar dados fora do Brasil e têm políticas próprias.
- Títulos, autor e descrição são exibidos apenas quando necessários ao fluxo.
  Títulos também são usados nos nomes dos arquivos salvos.
- Arquivos MP4 locais são processados pelo FFmpeg no próprio computador.
- Não são solicitados cookies de navegador, credenciais ou autenticação pessoal.
  Bibliotecas e processos auxiliares podem manter seus próprios caches técnicos.

## Armazenamento e exclusão

Os resultados ficam em:

- Linux: `${XDG_DATA_HOME:-~/.local/share}/youtube-converter/`.
- Windows: `%LOCALAPPDATA%\youtube-converter`.
- Alternativa: diretório indicado em `YOUTUBE_CONVERTER_DATA_DIR`.

As subpastas são `videos`, `audios` e `gifs`. Os arquivos permanecem até o usuário
excluí-los; o aplicativo não envia esses resultados a um servidor próprio.
Temporários ficam em diretórios exclusivos e são removidos ao concluir,
falhar ou cancelar normalmente. Interrupções abruptas (queda de energia, encerramento
forçado) podem deixá-los no disco; remova pastas `.download-*` e `.convert-*`
quando o aplicativo não estiver em execução. A exclusão comum não é apagamento
seguro de disco e não elimina cópias em backups ou sincronizadores externos.

Nenhum log em arquivo é criado por esta versão. Mensagens de erro não incluem
URLs, títulos, caminhos ou detalhes das exceções. Versões antigas podem ter
criado `app.log` junto ao programa: revise e exclua esse arquivo manualmente,
caso não precise mais dele. Arquivos antigos não são apagados automaticamente.

Para remover os dados do aplicativo, exclua as mídias e os temporários na pasta
configurada. Verifique também downloads antigos na pasta do projeto e backups.
Para exercer direitos sobre dados tratados pelo YouTube/Google, consulte os
canais de privacidade daquele serviço.

## Uso e limites

Baixe e processe apenas conteúdo para o qual tenha autorização. Mídias e
metadados podem conter dados pessoais de terceiros. Não publique esses dados
ou os inclua em commits sem uma finalidade legítima e autorização apropriada.

Estas medidas apoiam os princípios de necessidade, transparência, segurança e
prevenção do [art. 6º da LGPD](https://normas.leg.br/?urn=urn:lex:br:federal:lei:2018-08-14;13709!art6).
Elas não certificam conformidade jurídica. Quem operar o software como serviço
ou em uma organização deve avaliar o enquadramento aplicável, a base legal,
responsabilidades, direitos dos titulares, retenção, segurança e transferências
internacionais antes de tratar dados de outras pessoas.
