# Conteúdo das abas do plano

Cada pasta é uma aba, na ordem do número (`01-introducao`, `02-referencial`…). Para criar uma aba, crie uma pasta
nova com o número da posição; para mudar a ordem, troque os números.

```
01-introducao/
  _aba.yaml        título, subtítulo, cabeçalho, capítulo e tempo da aba
  simples/         modo simples (padrão): o roteiro dos slides, uma seção por slide
    01-acompanhe-e-baixe.yaml
    02-agenda.yaml
  completo/        modo completo: o conteúdo detalhado
    01-acompanhe-e-baixe.yaml
```

O botão discreto no cabeçalho de cada aba alterna os dois modos. Se uma aba não tiver uma das pastas, o modo que
falta mostra a outra.

## Seção

Um arquivo `.yaml` por seção, na ordem do número no nome. O nome do arquivo não aparece no site.

```yaml
titulo: 6.6 Estimativa de demanda      # botão da seção e título no topo
descricao: Resultado do objetivo (iii)  # opcional, abaixo do título
fonte: Bloco B3; Tabela 3              # opcional, no pé da seção ("Fonte: ...")
blocos:
- tipo: chamada
  texto: Uma frase em destaque, no cartão escuro.
```

Para editar, mude só o texto depois dos dois-pontos e mantenha os recuos. Texto que começa com aspas, `-`, `#`, `{`
ou `[`, ou que tem `: ` no meio, vai entre aspas simples (`'Objetivo (ii): praça'`). Números como `'834'` ficam
entre aspas para não perder o formato.

## Tipos de bloco

| tipo | campos |
|---|---|
| `chamada` | `texto`; `rotulo` opcional (texto pequeno acima) |
| `kpis` | `itens`: `rotulo`, `valor`, `detalhe`; `centralizar: true` centraliza |
| `cartoes` | `colunas` (2 a 5); `itens`: `rotulo`, `titulo`, `texto`, `lista` (itens com `-`), `destaque`; `centralizar: true` centraliza e aumenta o título |
| `texto` | `paragrafos`: um item por parágrafo; `nota` opcional |
| `lista` | `itens` |
| `passos` | `itens`: `titulo`, `texto` |
| `tabela` | `id`: o número da tabela ou quadro do TMin (`Tabela 5`, `Quadro 7`); o conteúdo vem de `tabelas.json` (`pnpm run tabelas`) |
| `abas` | `itens`: `id`, `rotulo` e `blocos` (outros blocos dentro de cada aba) |
| `barras` | gráfico de barras: `titulo`, `dados` (`rotulo`, `valor`), `unidade`, `decimais`, `fonte` |
| `qrcode` | sem campos: QR code do site |
| `downloads` | sem campos: arquivos para baixar (lista em `downloads.json`, gerada no build) |
