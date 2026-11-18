# Webscripts de coleta (TCC Luderia)

Scripts do Tampermonkey que repetem, no navegador de qualquer pessoa, as coletas em sites feitas para o TCC. Cada um abre um painel no canto superior direito da página, lê o que o site mostra e baixa um CSV (separador `;`, UTF-8 com BOM). Nada é enviado para fora do navegador.

## Instalar

1. Instalar a extensão [Tampermonkey](https://www.tampermonkey.net/) (Chrome, Edge, Vivaldi ou Firefox).
2. Abrir o endereço "raw" do script desejado, na pasta [`_instalaveis/`](_instalaveis/), e clicar em **Instalar**:
   `https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis/<script>.user.js`
3. Abrir o site da coleta. O painel aparece sozinho.

O instalável já traz a lista de alvos da pesquisa (casas, perfis, buscas, itens) e se atualiza pelo Tampermonkey. Para coletar outra população, editar `lista_<script>.js` e regerar (`python3 _src/outros/G5_outros/gerar_instalaveis.py`).

## Scripts

| Script | Site | O que coleta | Bloco e destino do CSV | Uso no TCC |
|---|---|---|---|---|
| `maps_busca` | Google Maps | Resultados das buscas "<termo> em <cidade>" (15 termos × 28 cidades): nome, place_id, nota, nº de avaliações, categoria, endereço, coordenada | B1, `dados-brutos/B1_estabelecimentos/busca_maps/` | Descoberta dos estabelecimentos, a população (3.2 e cap. 5) |
| `maps_ficha` | Google Maps | Ficha de cada casa: nota, nº de avaliações, categoria, situação, endereço, coordenada, site, telefone e horário por dia | B1, `dados-brutos/B1_estabelecimentos/ficha_maps/` | Recorte por avaliações e horário de funcionamento (caps. 5 e 7) |
| `maps_avaliacoes` | Google Maps | Avaliações com texto de cada casa (nota, data relativa, texto, fotos, resposta), com autor pseudonimizado | B2, `dados-brutos/B2_avaliacoes/coletas/` | Proposta de valor, reclamações, gasto (caps. 5 e 6) |
| `maps_horarios_pico` | Google Maps | Gráfico "Horários de pico" de cada casa: ocupação relativa por dia e hora | B1, `dados-brutos/B1_estabelecimentos/horarios_pico/` | Curva de fluxo e horário de funcionamento (caps. 6 e 7) |
| `maps_entorno` | Google Maps | Metrô, trem, VLT e shoppings no entorno de cada casa, com distância e avaliações | B1, `dados-brutos/B1_entorno/` | Critérios do ponto (5.4 e 6.4) |
| `instagram` | Instagram | Dados do perfil e posts do período (data, curtidas, comentários, legenda, possível evento) | B1, `dados-agregados/B1_redes_sociais/` | Comunicação e eventos dos concorrentes (caps. 5 e 6) |
| `instagram_snowball` | Instagram | Lista "seguindo" de cada semente | B1, `dados-brutos/B1_redes_sociais/seguindo/` (fora do git: tem @ de pessoas) | Descoberta de casas por bola de neve (3.2) |
| `cardapio` | Sites de cardápio digital | Itens, preços, seções e categorias | B1, `dados-brutos/B1_cardapios/` | Preços e cesta dos concorrentes (cap. 5) |
| `acervo` | Ludopedia, Acervo de Jogos, rejoy | Títulos do acervo de cada casa e preço de aluguel | B1, `dados-brutos/B1_acervo_jogos/acervos_luderias/` | Tamanho e composição do acervo (cap. 5) |
| `aluguel` | OLX, ZAP, Viva Real, NetImóveis, QuintoAndar | Anúncios de aluguel comercial (preço, condomínio, IPTU, área, bairro) | B5, `dados-brutos/B5_aluguel/` | Aluguel e condomínio (C04 e C05, cap. 9) |
| `mobiliario` | Amazon, Magalu, Leroy Merlin e outras lojas | Ofertas de cada item do orçamento (preço, frete, unidades) | B5, `dados-brutos/B5_mobiliario/` e `B5_reforma/` | Investimento inicial (9.3) |

O que cada script lê em cada site, as regras e a data em que a leitura foi conferida estão no comentário de abertura do arquivo. Os sites mudam: se o painel avisar que não achou a lista ou os seletores, a leitura precisa ser revista.

## Usar

- **Menu de alvos:** o seletor traz os alvos da pesquisa por grupo, com `✓` coletado, `◐` parcial, `!` refazer e `○` falta. Escolher um abre a página e coleta; **Próximo** vai ao seguinte que falta.
- **Botões:** os de ação têm ícone e uma palavra; os demais, só ícone. Parar o mouse sobre qualquer botão, selo ou `ⓘ` mostra o que ele faz.
- **Cores:** roxo em curso, verde concluído, âmbar interrompido ou a conferir, vermelho erro. O ponto do cabeçalho mostra o estado mesmo com o painel minimizado.
- **Perguntas** (refazer, substituir a fila) aparecem numa faixa âmbar no topo do painel: `✓` ou Enter confirma, `✗` ou Esc cancela.
- **Lixeira:** em dois cliques, baixa um backup e zera a coleta guardada no navegador.
- **Captcha ou bloqueio do site:** o script para e avisa; nunca tenta resolver.

Depois da coleta, o CSV vai para a pasta indicada na dica do botão de download, e o script `2_build` da coleta em `_src/pyScripts/` gera as tabelas de `dados-agregados/`.

## Coletas sem webscript

As bases públicas do B4 (IBGE, BCB, Novo CAGED, FipeZap, CONCLA, Planalto) e o SINAPI são baixados por scripts Python sem chave de acesso (`_src/pyScripts/B4_*/1_collect/` e `B5_Reforma/1_collect/`), que já são replicáveis. A contagem do B3 é presencial.

A descoberta e a ficha dos estabelecimentos (B1) foram coletadas pela API paga do Google Places (`B1c_places.py`, `B1c_details.py`); o `maps_busca` e o `maps_ficha` repetem as duas no site, sem chave. A lista do site não é idêntica à da API (ordem pela área do mapa, até cerca de 120 resultados contra 60), e o horário lido é o da semana da coleta: o conjunto de candidatos pode diferir do coletado em setembro de 2026.

## Desenvolver

- Regras comuns: [`specs/especificacoes_comuns.md`](specs/especificacoes_comuns.md). Painel: [`_kit_painel/kit_painel.js`](_kit_painel/kit_painel.js), copiado para cada script por `node _src/webScripts/_kit_painel/embutir.js`.
- Testes: `node --test <script>.test.cjs` na pasta do script (o do `mobiliario` precisa de `pnpm install` em `B5_ativos_fixos/`).
- Ver um painel sem abrir o site: `python3 -m http.server 8791 --directory _src/webScripts` e abrir `http://localhost:8791/_kit_painel/demo.html?script=acervo`.
- Depois de mudar um script, a lista ou o kit: `embutir.js`, os testes e `gerar_instalaveis.py`.
