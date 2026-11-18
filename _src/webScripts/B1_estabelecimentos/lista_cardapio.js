// lista_cardapio.js: itens do menu do cardapio.user.js (Coletor de cardápios).
// O carregador do Tampermonkey lê este arquivo (@require) antes do script; editar aqui
// muda o menu no próximo recarregar da página, sem reinstalar.

// ---------- menu dos cardápios ----------
// População: as 63 casas do B1 (lista_maps_horarios_pico.js, de B1_horarios.csv), por capital.
// url: cardápio digital conhecido que abre como página (B1_cardapios_digitais_itens.csv,
// B1_cardapios_busca_profunda.csv e B1_busca_minuciosa_taxa_cardapio_acervo.csv); vazia quando
// não há, e aí escolher a casa busca o nome dela só no site aberto (iFood) ou, nos demais, deixa
// a casa escolhida para procurar ali e vincular pelo "+". antes: itens com preço já no
// B1 por qualquer fonte (digital, PDF, prints, OCR) e a data do cardápio
// (B1_resumo_estabelecimentos.xlsx, abas estabelecimentos e cesta, 16/11/2026).
// Casas acrescentadas pelo botão "Adicionar" do painel ficam no navegador até virem para cá.
// [id, casa, capital, url, antes: [itens, data] ou null]
var LISTA_CARDAPIO = [
  ['bardo_mago', 'Bardo Mago', 'Belo Horizonte', 'https://www.vucafood.com.br/funminds/2219/cardapio-digital', [112, '02/2026']],
  ['comdado_bar_e_jogos', 'Comdado Bar e Jogos', 'Belo Horizonte', '', [55, '12/2025']],
  ['garagem_do_nerd', 'Garagem do Nerd', 'Belo Horizonte', 'https://garagemdonerd.com.br/cardapio/', [1, '23/06/2024']],
  ['la_tabuleria', 'La Tabuleria', 'Belo Horizonte', 'https://latabuleria.saipos.com/home', [90, '']],
  ['ludocafe', 'LudoCafé', 'Belo Horizonte', '', [13, '16/11/2024']],
  ['shelf_bar_e_jogos', 'Shelf Bar e Jogos', 'Belo Horizonte', '', [138, '']],
  ['ludoteca_sidequest', 'Ludoteca Sidequest', 'Belém', '', [58, '']],
  ['fortaludica_burgers_jogos', 'FORTALÚDICA - BURGERS & JOGOS', 'Brasília', '', [53, '05/2026']],
  ['gruta_bsb', 'Gruta BSB', 'Brasília', '', null],
  ['inside_games', 'Inside Games', 'Brasília', '', [24, '09/2026']],
  ['loja_de_jogos_asgard', 'Loja de Jogos - Asgard', 'Brasília', '', [39, '']],
  ['ludoteca_bgc', 'Ludoteca BGC', 'Brasília', '', [60, '08/2026']],
  ['utopia_games_food', 'Utopia Games & Food', 'Brasília', '', [32, '']],
  ['metropoly_bar', 'Metropoly Bar', 'Campinas', 'https://www.deliway.com.br/metropoly-bar-delivery-campinas-sp', [149, '']],
  ['muito_geek', 'Muito Geek | TCG • Board Games • Fliperama', 'Campinas', '', null],
  ['nergeek', 'Nergeek', 'Campinas', '', null],
  ['alcapao_jogos', 'Alçapão Jogos', 'Curitiba', '', [26, '']],
  ['boardz_game_pub', 'BoardZ Game Pub', 'Curitiba', '', [93, '']],
  ['joyjoy_cafe', 'Joyjoy Café', 'Curitiba', '', [2, '01/08/2024']],
  ['paladino_hobbies', 'Paladino Hobbies', 'Curitiba', '', null],
  ['taverna_game_house', 'Taverna Game House', 'Curitiba', '', null],
  ['vila_celta_hobby_store_jogos_e_cafe', 'Vila Celta Hobby Store - Jogos e Café', 'Curitiba', '', [2, '04/2024']],
  ['ccg_floripa', 'CCG Floripa', 'Florianópolis', '', [7, '07/2023']],
  ['chef_on_play', 'Chef on Play', 'Florianópolis', '', [73, '01/2026']],
  ['cineplay_restaurante_e_jogos', 'Cineplay- Restaurante e Jogos', 'Florianópolis', '', [112, '06/2024']],
  ['balboa_s_hobby_games', 'Balboa\'s Hobby Games', 'Fortaleza', '', [38, '01/2026']],
  ['dominaria_cards_games', 'Dominaria Cards & Games', 'Fortaleza', '', null],
  ['paladins_game_store', 'Paladins Game Store', 'Goiânia', '', null],
  ['arcadea_gaming_pub', 'Arcadea Gaming Pub', 'Porto Alegre', '', [95, '10/2026']],
  ['toca_do_rato', 'Toca do Rato - Pizzaria e Jogos de Tabuleiro', 'Porto Alegre', 'https://tocadoratopizzasejogos.saipos.com/home', [26, '10/2025']],
  ['nala_land_bar_de_jogos_de_tabuleiro_em_r', 'Nala Land - Bar de Jogos de Tabuleiro em Recife', 'Recife', '', [28, '04/2026']],
  ['cheio_de_fome', 'Cheio de Fome - Vila da Penha', 'Rio de Janeiro', 'https://pedido.anota.ai/loja/cheio-de-fome-vila-da-penha-1', [194, '']],
  ['game_of_boards', 'Game Of Boards', 'Rio de Janeiro', 'https://www.ifood.com.br/delivery/rio-de-janeiro-rj/game-of-boards---ludobar--pizzaria-botafogo/', [2, '16/10/2026']],
  ['luderia_carioca', 'Luderia Carioca', 'Rio de Janeiro', '', [37, '04/2026']],
  ['magic_store_brazil', 'Magic Store Brazil', 'Rio de Janeiro', '', null],
  ['red_jogos', 'RED jogos', 'Rio de Janeiro', '', null],
  ['reduto', 'Reduto', 'Rio de Janeiro', '', null],
  ['tabuclub', 'TabuClub', 'Rio de Janeiro', '', [77, '01/2026']],
  ['sao_jogue_bela_vista', 'São Jogue - Bela Vista', 'Salvador', 'https://sao-jogue.goomer.app/', [56, '10/2026']],
  ['60_minutos_escape_hamburgueria_e_boardga', '60 Minutos Escape, Hamburgueria e Boardgames', 'São Paulo', '', null],
  ['arena_bg', 'Arena BG | Jogos de Tabuleiro | Hamburgueria', 'São Paulo', '', [65, '']],
  ['bodogami_restaurante_e_cafeteria', 'Bodogami Restaurante e Cafeteria', 'São Paulo', '', [91, '11/2026']],
  ['bravo_jogos', 'Bravo Jogos', 'São Paulo', '', null],
  ['chq_jogos', 'CHQ Jogos', 'São Paulo', '', null],
  ['cartola_luderia_bar', 'Cartola Luderia Bar', 'São Paulo', '', [51, '07/2025']],
  ['castelos_bar_boardgames', 'Castelos Bar & Boardgames', 'São Paulo', '', [67, '03/2024']],
  ['coletivo_geek', 'Coletivo Geek', 'São Paulo', '', [71, '05/2026']],
  ['covil_game_bar', 'Covil Game Bar', 'São Paulo', '', [73, '07/2025']],
  ['covil_game_bar_sbc', 'Covil Game Bar SBC', 'São Paulo', '', [73, '07/2025']],
  ['dungeon_games_store', 'Dungeon Games Store', 'São Paulo', '', [42, '']],
  ['encounter', 'Encounter | Jogos de Tabuleiro | Board Games', 'São Paulo', '', [26, '01/2026']],
  ['espaco_162_meu_karaoke_box', 'Espaço 162 - Meu Karaokê Box', 'São Paulo', '', [61, '02/2024']],
  ['fan_hour', 'Fan Hour Games and Burgers', 'São Paulo', 'https://qrco.de/bdUhFc', [52, '03/11/2026']],
  ['flow_games_burgers_cards_comunidade', 'Flow Games - Burgers, Cards & Comunidade', 'São Paulo', '', [16, '08/2025']],
  ['jogasampa', 'Jogasampa', 'São Paulo', '', [7, '10/2023']],
  ['ludus_luderia', 'Ludus Luderia', 'São Paulo', '', [164, '03/2026']],
  ['omniverse', 'OMNIVERSE', 'São Paulo', '', null],
  ['pitta_s_board_games', 'Pitta\'s Board Games', 'São Paulo', '', null],
  ['place_games', 'Place Games', 'São Paulo', '', [56, '07/2026']],
  ['play_easy', 'Play Easy', 'São Paulo', '', [16, '']],
  ['tubaleria', 'Tubaleria', 'São Paulo', '', [17, '05/2026']],
  ['xplace', 'XPlace', 'São Paulo', '', null],
  ['cafe_geek_cafeteria_e_ludoteca', 'Café Geek Cafeteria e Ludoteca', 'Vitória', '', [70, '05/2026']],
];
