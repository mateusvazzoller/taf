# CLAUDE.md — contexto do projeto

App de acompanhamento de treino para o **TAF da Polícia Civil do Paraná**.
Uso pessoal do dono do repositório, que está se preparando para a prova física.
O treino foi prescrito por um profissional de educação física — **não invente,
não "corrija" e não complete exercícios ou cargas por conta própria.** O que
está no app tem que espelhar a planilha; qualquer dúvida vira pergunta ao
usuário, não suposição.

## Origem dos dados

Planilha `TAF SEMANAS 1A4.xlsx`, aba `Plan1`, em `C:\Users\User\Documents\Treino\`
(fora do repositório — é documento pessoal, não subir). Estrutura dela: coluna A
tem os dias, e as semanas 1 a 4 ocupam as colunas C, G, K e O.

Cinco sessões por semana:

| Dia | Sessão | Foco |
|---|---|---|
| 1 | Academia 1 | Inferior, potência, tornozelos |
| 2 | Extra 1 | Abdômen e corrida |
| 3 | Academia 2 | Superior, corda, barra |
| 4 | Extra 2 | Abdômen e corrida |
| 5 | Extra 3 | Barra, remador, corrida |

O bloco cobre **apenas as semanas 1 a 4** — decisão do usuário. Ao terminar as
cinco sessões da semana 4, o app mostra um aviso de fim de bloco em vez de
reiniciar o ciclo. Semanas 5 em diante só entram quando o professor passar.

## Arquivos

| Arquivo | Papel |
|---|---|
| `index.html` | **Fonte única da verdade.** O app inteiro: dados do treino, estilos e lógica |
| `manifest.webmanifest` | Nome, cores e ícones da instalação |
| `sw.js` | Service worker — funcionamento offline |
| `icons/` | Ícones PNG, gerados por `tools/gerar-icones.py` |
| `sons/` | Avisos sonoros em MP3 + `CREDITOS.txt` com autoria e licença |
| `tools/gerar-icones.py` | Regera os ícones a partir das cores do app |
| `tools/build-artifact.py` | Gera a versão para publicar como Artifact do Claude |

Não existe build, bundler nem dependência. Editar `index.html` e dar push é o
fluxo completo.

## Estrutura do `index.html`

Tudo em um arquivo só, nesta ordem: `<style>` com os tokens e componentes, o
HTML da casca, e um `<script>` com uma IIFE contendo dados, estado e render.

### Dados do treino — `PLAN`

Array de 5 sessões. Cada sessão tem `blocos`, e cada bloco tem `sem`: um array
de **exatamente 4 posições**, uma por semana.

```js
{ id:"b2", t:"Agachamento búlgaro", tipo:"Complexo", nota:"…", sem:[ cfgS1, cfgS2, cfgS3, cfgS4 ] }
```

Cada `cfg` de semana:

| Campo | O que é |
|---|---|
| `s` | Número de séries (vira a quantidade de chips marcáveis) |
| `r` | Descanso em segundos que alimenta o timer |
| `rt` | Descanso como está escrito na planilha, ex. `"1:00 a 2:00 entre os tiros"` |
| `ritmo` | Só para EMOM — substitui a etiqueta de descanso e troca "séries" por "rodadas" |
| `it` | Exercícios: `{ n:nome, p:prescrição, reg:{t:tipo} }` |

Helpers: `eq(x)` repete a mesma config nas 4 semanas, `pair(a,b)` faz
semanas 1-2 com `a` e 3-4 com `b`. A maior parte da progressão da planilha é
1-2 igual e 3-4 igual, daí o `pair`.

**Distinção que importa:** `rt` é o que a planilha manda e aparece com a
etiqueta "Descanso" destacada; quando o bloco não tem `rt`, o `r` é sugestão
nossa e aparece só como tempo. Não apresente sugestão como prescrição.

### Registros — `REG`

Tipos de campo que o usuário preenche: `kg`, `reps`, `seg`, `tempo` (mm:ss),
`m`. Os de tempo (`seg`, `tempo`) ganham botão de cronômetro que preenche o
campo sozinho ao salvar.

### Vídeos — `VID` e `VIDEO`

`VID` é o mapa `nome do exercício → termos de busca` (fallback). `VIDEO` é o
mapa curado `nome do exercício → {id, t, c, d}` (id do YouTube, título, canal,
duração) que alimenta o player embutido no painel ▶. Prioridade ao abrir:

1. Link salvo pelo usuário (`S.vid`) — se for do YouTube, também toca embutido.
2. Vídeo curado de `VIDEO` — player embutido + crédito do canal + link externo.
3. Busca no YouTube com os termos de `VID`, em outra aba.

**Não inventar IDs.** Todos os IDs de `VIDEO` foram encontrados por busca real
e verificados um a um via oEmbed (que também acusa vídeo com incorporação
desativada) em 10/08/2026. Ao trocar um vídeo, verifique o novo do mesmo jeito.
O iframe (`youtube-nocookie.com`) é criado só quando o painel abre e é removido
ao fechar — o áudio para e nada fica carregado por trás. O player precisa de
internet; o restante do app segue funcionando offline. Exercícios sem entrada
nos mapas não ganham ícone (corrida, sprint e bike ficaram de fora de
propósito).

### Simulado do TAF — `PROVAS` e `S.taf`

Aba própria (`S.tab === "sim"`, render em `renderSim()`). `PROVAS` lista as
cinco provas com `dir` (1 = quanto maior melhor; -1 = quanto menor melhor,
caso do shuttle run), `bool` para a corda (subiu / não subiu) e `timer`
opcional que abre o cronômetro já no tempo da prova (1:00 no abdominal,
12:00 na corrida).

**As metas são digitadas pelo usuário, nunca embutidas no código.** Os
índices mínimos mudam por idade e sexo e saem do edital da PCPR — o app só
compara o resultado com o número que ele colocou em "Meta do edital". Não
invente esses valores, nem como sugestão.

`S.taf = { metas:{idProva: "valor"}, tests:[{p, v, d, ts}] }`. O veredito
sai de `passou()`, que devolve `null` quando não há meta.

### Estado — `S` e `localStorage`

Chave `taf-pcpr-v1`. Campos persistidos listados em `FIELDS`; `snapshot()` monta
o objeto exportado. Formato das chaves:

```
done  →  "w{semana}|{idSessao}|{idBloco}|{indiceSerie}"
logs  →  "w{semana}|{idSessao}|{idBloco}|{indiceExercicio}|{indiceSerie}"
sess  →  "w{semana}|{idSessao}"     (concluída: data, contagem, dur, rpe)
notas →  "w{semana}|{idSessao}"
ini   →  "w{semana}|{idSessao}"     (Date.now da 1ª série — tempo do treino)
vid   →  "{nome do exercício}"
taf   →  { metas, tests }           (simulados; não é por semana)
```

Em `cfg`: `prova` (data do TAF, "AAAA-MM-DD", liga a contagem regressiva) e
`somTipo` (qual arquivo de `sons/` toca).

Ao acrescentar campo novo, lembre que backup antigo não o tem — `tafInit()`
existe para preencher o que falta na importação.

Tudo fica no aparelho. **Não há sincronização entre celulares** — é o preço de
funcionar offline sem servidor. A saída é ⚙ Ajustes → Exportar/Importar backup.

Se você mudar o formato das chaves, o histórico do usuário quebra. Nesse caso é
obrigatório migrar os dados antigos ou trocar a versão da chave e converter.

## Decisões que não devem ser desfeitas

**Aviso sonoro é gravação, não síntese.** A primeira versão gerava os bipes
com osciladores (onda quadrada, depois senoide com harmônico). O usuário
rejeitou as duas: "toque monofônico é muito feio". Hoje cada opção é um MP3
curto em `sons/`, tocado por Web Audio a partir de um `AudioBuffer` — o
mesmo arquivo serve para tudo: inteiro no fim do descanso, os primeiros
0,55 s como confirmação, os primeiros 0,13 s na contagem 3-2-1. A síntese
sobrou só como reserva se o arquivo não carregar.

Ao trocar um som, **confira onde o som começa de fato** (envelope de
energia, não confie no nome do arquivo). O despertador original tem 2
segundos de tique-taque antes da campainha, e o primeiro recorte pegou
justamente o silêncio. Como a contagem 3-2-1 toca só os 130 ms iniciais, um
arquivo que começa devagar sai mudo. Iguale também o volume **médio**
(≈ −16 dBFS) e não o de pico, senão uma opção parece muito mais baixa que
as outras. Os arquivos ficam em `ARQUIVOS` no `sw.js` para tocarem offline.

**Atualização avisa em vez de trocar em silêncio.** App instalado na tela
inicial pode ficar semanas com a versão velha. O app chama `reg.update()`
toda vez que volta para a frente (`visibilitychange`) e, quando o service
worker novo assume, mostra a faixa `#upd`. Cuidado com a lógica de
`jaControlado`: a **primeira** troca de controlador é a instalação inicial e
não deve virar aviso, mas a partir dela toda troca é atualização de verdade
— um bug real morava aí. Ajustes mostra a versão instalada perguntando ao
service worker por `postMessage`.

**Cronômetro usa `Date.now()`, não `requestAnimationFrame`.** A primeira versão
acumulava deltas de rAF e o timer congelava quando a tela apagava ou o usuário
trocava de app — inaceitável para descanso de treino. Hoje `T.anchor` guarda o
instante alvo e o tempo é sempre derivado do relógio; `setInterval` só redesenha.
Voltar para rAF reintroduz o bug. **O tempo total do treino segue a mesma
regra**: `S.ini` guarda o instante da primeira série e o total é sempre
`agora − início`, então fechar o app no meio não atrapalha.

**Ícone ▶ abre o painel com player embutido** (decisão revista em 10/08/2026 a
pedido do usuário — antes era só busca em outra aba). O embed é um iframe do
YouTube criado sob demanda; não há CDN nem biblioteca de player. Em `file://`
o embed do YouTube não funciona (erro 153) — testar sempre via servidor local
ou no site publicado.

**O botão de instalar não promete o que não pode cumprir.** No iOS a Apple não
permite instalação programática — o botão mostra o passo a passo do Safari. No
Android ele dispara o `beforeinstallprompt` quando o Chrome oferece. Detecta
também se está dentro de um iframe/webview e avisa para abrir no navegador, que
é a causa nº 1 de "não instala".

**Tema claro e escuro via tokens.** Os componentes só usam variáveis CSS; o tema
é redefinido em `@media (prefers-color-scheme)` e nos seletores
`:root[data-theme]`. Nunca estilizar componente dentro do media query — já deu
colisão de especificidade uma vez (estado de série concluída), resolvida com o
token `--on-good`. Desde 10/08/2026 há um seletor manual em Ajustes
(Auto/Claro/Escuro, `S.cfg.tema`, aplicado por `applyTheme()` via
`data-theme` no `<html>`); "Auto" segue o sistema e também atualiza o
`<meta name="theme-color">`.

## Publicar uma alteração

```bash
cd "C:/Users/User/Documents/Treino/taf-site" && git add -A && git commit -m "…" && git push
```

O Pages reconstrói sozinho em 30 a 60 segundos.

**Ao alterar `index.html`, troque a versão em `sw.js`** (`const VERSAO = "taf-v1"`
→ `"taf-v2"`). Sem isso, quem já instalou pode continuar com a versão velha em
cache. É o erro mais fácil de cometer aqui.

- Site: https://mateusvazzoller.github.io/taf/
- Repositório: https://github.com/mateusvazzoller/taf
- Artifact (versão antiga, opcional): `tools/build-artifact.py` regenera

## Como testar

Service worker e manifest **não funcionam em `file://`**. Suba um servidor:

```bash
cd "C:/Users/User/Documents/Treino/taf-site" && python -m http.server 8765 --bind 127.0.0.1
```

Depois abra `http://127.0.0.1:8765/` e confira no console: service worker ativo,
manifest válido, cache populado. Para provar o offline, derrube o servidor e
recarregue a página — o app tem que abrir inteiro.

Vale varrer as 20 combinações de semana × sessão comparando com a planilha
antes de publicar mudança nos dados do treino.

## Pendências

- **Bloco "4x25\" esforço máximo" (Extra 2, bloco 2):** a planilha não diz o
  aparelho. Está sinalizado como aviso dentro do bloco. Quando o usuário
  confirmar com o professor, corrigir e remover a `nota`.
- **Semanas 5 a 8:** não existem ainda. Quando chegarem, estender o array `sem`
  de cada bloco e o seletor de semanas — hoje `renderHead()` e a checagem de fim
  de bloco assumem 4.

## Como falar com o usuário

Português do Brasil. Ele não é programador: explique em termos do que acontece
na tela e no celular, não em termos de código. Ele valoriza saber o que **não**
funciona e por quê — limitação do iOS, dado que não sincroniza, repositório
público. Não prometa o que a plataforma não entrega.
