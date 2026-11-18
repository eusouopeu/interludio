// lista_maps_busca.js: itens do menu do maps_busca.user.js (Busca de estabelecimentos no Maps).
// O carregador do Tampermonkey lê este arquivo (@require) antes do script; editar aqui
// muda o menu no próximo recarregar da página, sem reinstalar.

// Termos e cidades da etapa 1 do B1 (_src/pyScripts/B1_Estabelecimentos/1_collect/B1c_places.py):
// os 15 termos de busca e as 27 capitais, mais Campinas (15ª metrópole da REGIC 2018, a única
// que não é capital). Cada busca é "<termo> em <cidade>", como na coleta pela Places API.
// cidades: [cidade, UF]
var LISTA_MAPS_BUSCA = {
  termos: [
    "ludobar", "luderia", "ludoteca", "quiz bar", "board game bar", "board game café",
    "café de jogos de tabuleiro", "bar de jogos de tabuleiro", "jogos de tabuleiro",
    "loja de jogos de tabuleiro", "loja de board game", "loja de card game", "loja de RPG",
    "board game", "clube de jogos de tabuleiro",
  ],
  cidades: [
    ["Rio Branco", "AC"], ["Maceió", "AL"], ["Macapá", "AP"], ["Manaus", "AM"], ["Salvador", "BA"],
    ["Fortaleza", "CE"], ["Brasília", "DF"], ["Vitória", "ES"], ["Goiânia", "GO"], ["São Luís", "MA"],
    ["Cuiabá", "MT"], ["Campo Grande", "MS"], ["Belo Horizonte", "MG"], ["Belém", "PA"],
    ["João Pessoa", "PB"], ["Curitiba", "PR"], ["Recife", "PE"], ["Teresina", "PI"],
    ["Rio de Janeiro", "RJ"], ["Natal", "RN"], ["Porto Alegre", "RS"], ["Porto Velho", "RO"],
    ["Boa Vista", "RR"], ["Florianópolis", "SC"], ["São Paulo", "SP"], ["Aracaju", "SE"],
    ["Palmas", "TO"], ["Campinas", "SP"],
  ],
};
