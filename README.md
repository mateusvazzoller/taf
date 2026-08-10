# TAF · Treino Semanas 1 a 4

App de acompanhamento da preparação física para o TAF da Polícia Civil do Paraná.
Roda no navegador do celular, instala na tela inicial e funciona sem internet.

## O que tem

- As 5 sessões da semana (Academia 1, Extra 1, Academia 2, Extra 2, Extra 3) nas semanas 1 a 4
- Marcação de séries com progresso por sessão e por semana
- Timer de descanso automático e cronômetro para isometrias
- Registro de cargas, tempos, repetições e distâncias, com comparação entre as semanas
- Vídeo demonstrativo embutido em cada exercício (precisa de internet), com espaço para salvar o link do professor — que tem prioridade
- Exportar e importar backup dos dados

## Como funciona

Uma página só, sem servidor e sem banco de dados. Tudo o que você marca fica
guardado no próprio aparelho (`localStorage`), então:

- Os dados não saem do celular e ninguém mais tem acesso a eles.
- Cada aparelho tem o próprio histórico — não sincroniza entre celulares.
- Limpar os dados do navegador apaga o histórico. Use *Exportar backup*.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `index.html` | O app inteiro — marcação, timers, registros e dados do treino |
| `manifest.webmanifest` | Nome, cores e ícones usados na instalação na tela inicial |
| `sw.js` | Service worker: guarda o app no aparelho para abrir sem internet |
| `icons/` | Ícones do atalho |
| `tools/` | Scripts para regerar os ícones e a versão publicada como Artifact |
| `CLAUDE.md` | Contexto do projeto: estrutura, decisões e como alterar sem quebrar |

## Publicando

Serve qualquer hospedagem de site estático. No GitHub Pages: *Settings* →
*Pages* → *Deploy from a branch* → `main` / `root`.

Ao alterar o app, troque o número da versão em `sw.js` (`const VERSAO = "taf-v1"`)
para que os celulares que já instalaram recebam a atualização.

## Aviso

Esta rotina foi prescrita por um profissional de educação física para um aluno
específico, considerando o condicionamento dele. Não é um programa genérico:
quem for usar deve passar por avaliação antes.
