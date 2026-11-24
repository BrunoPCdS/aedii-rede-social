# Relatório do Projeto — Rede Social Simplificada

## Integrantes

- Bruno Pinto Corrêa da Silva
- Lucas Cunha Rocha

## 1. O que foi feito

O programa implementa as consultas pedidas nas seções 3.1 a 3.7 do README:

- Busca de perfil por `@usuario`, com totais de seguidos, seguidores e posts.
- Sugestões de usuários a distância dois, priorizadas por conexões em comum.
- Componentes conexos e usuários isolados, tratando as conexões como não dirigidas.
- Busca de posts por intervalo inclusivo de datas, em ordem cronológica, exibindo a quantidade encontrada.
- Listas de usuários com mais seguidores e posts com mais curtidas.
- Ranking de engajamento, com desempate alfabético pelo nome de usuário.
- Interface de linha de comando com ajuda, validação de parâmetros, saída JSON e códigos de saída apropriados.

## 2. Organização do código

- `py/aedlib.py`: lê os três CSVs, sem alterar os arquivos de dados.
- `py/main.py`: ponto de entrada conforme os exemplos do README.
- `py/rede_social/estruturas.py`: implementa `TabelaHash`, `HeapMaxima`, `GrafoSeguidores`, `NoAVLDePosts`, `ArvoreAVLDePosts` e `OrdenadorMergeSort`.
- `py/rede_social/aplicacao.py`: monta os índices e executa as operações da rede social usando as estruturas próprias.
- `py/rede_social/interface.py`: interpreta os argumentos, valida entradas e imprime texto ou JSON.
- `py/rede_social/__init__.py`: declara o pacote Python.

As classes e funções receberam nomes em português que descrevem sua responsabilidade. A leitura dos CSVs fica separada dos algoritmos, e a interface fica separada das consultas.

## 3. Escolhas de implementação

### Tabela hash

A classe `TabelaHash` usa uma função polinomial de base 31 e encadeamento separado para colisões. O tamanho padrão é 4099 baldes. A estrutura indexa nomes de usuário e IDs, permitindo localizar registros e índices sem percorrer a lista completa.

### Grafo

`GrafoSeguidores` representa cada usuário por um índice e mantém listas de adjacência para quem ele segue e para quem o segue. As sugestões percorrem caminhos de duas arestas e contam conexões em comum. As comunidades usam BFS e percorrem as duas listas para tratar as relações como não dirigidas.

### Heap

`HeapMaxima` é uma heap binária de máximo: o item de maior prioridade fica na raiz. Os comandos top inserem os candidatos na heap e removem os maiores até chegar a `k` ou esgotar os itens.

### Árvore AVL

`ArvoreAVLDePosts` indexa os posts pela data e agrupa no mesmo nó os posts do mesmo dia. As rotações mantêm a árvore balanceada. A consulta de intervalo só desce para os ramos que podem conter datas dentro dos limites.

### Ordenação

`OrdenadorMergeSort` implementa Merge Sort. No ranking, ordena por engajamento decrescente e, em empate, por `@usuario` crescente. Também ordena os tamanhos das comunidades.

Não são usados `dict`, `set`, `heapq`, `sorted()`, `.sort()`, `bisect`, `collections` ou bibliotecas externas para implementar as estruturas solicitadas.

## 4. Complexidade

Considere `V` usuários, `E` conexões, `P` posts, `D` datas distintas, `k` resultados pedidos, `C` comunidades e `R` posts retornados. As complexidades abaixo descrevem cada consulta depois que os índices são carregados. Cada execução também inclui a preparação dos índices, que custa `O(V + E + P log D)` em média.

| Comando | Complexidade da consulta | Motivo |
|---|---:|---|
| `buscar @usuario` | `O(1)` média | Busca hash e consulta contagens já acumuladas. No pior caso, muitas colisões tornam a busca linear no balde. |
| `sugerir @usuario k` | `O(S + A + V log V)` | `S` é o número de contas seguidas pela pessoa e `A` é o total de arestas percorridas a partir dessas contas. A heap recebe até `V` candidatos. |
| `comunidades` | `O(V + E + C log C)` | BFS percorre vértices e conexões; Merge Sort ordena os tamanhos dos componentes. |
| `posts-entre data1 data2` | `O(log D + R)` | A AVL busca os ramos do intervalo e visita os posts encontrados. |
| `top-seguidos k` | `O(V log V + k log V)` | Insere usuários na heap e remove até `k` máximos. |
| `top-curtidos k` | `O(P log P + k log P)` | Insere posts na heap e remove até `k` máximos. |
| `ranking` | `O(V log V)` | Calcula o engajamento e ordena todos os usuários com Merge Sort. |

## 5. Testes executados

Os comandos foram executados no PowerShell, a partir da raiz do repositório. O `@usuario` foi colocado entre aspas simples para evitar interpretação especial do PowerShell.

| Caso | Comando | Resultado observado |
|---|---|---|
| Compilação | `python -m compileall -q py` | Concluiu sem erros. |
| Ajuda | `python py/main.py ajuda` | Exibiu comandos e exemplos; status 0. |
| Usuário existente | `python py/main.py buscar '@henrique_nascimento'` | Exibiu Henrique Nascimento, cadastro em 2022-10-26, 10 seguidos, 12 seguidores e 8 posts. |
| Sugestões | `python py/main.py sugerir '@henrique_nascimento' 3` | Retornou três sugestões; as duas primeiras tinham duas conexões em comum. |
| Comunidades | `python py/main.py comunidades` | Encontrou 76 componentes e 58 usuários isolados; tamanhos em ordem decrescente. |
| Data com posts | `python py/main.py posts-entre 2025-09-01 2025-09-01` | Retornou 23 posts e a quantidade 23. |
| Intervalo sem posts | `python py/main.py posts-entre 2024-01-01 2024-01-31` | Retornou quantidade 0 e lista vazia. |
| Top seguidos | `python py/main.py top-seguidos 3` | Retornou os três primeiros; maior contagem observada: 110 seguidores. |
| Top curtidos | `python py/main.py top-curtidos 3` | Retornou posts com 2988, 1274 e 789 curtidas. |
| Ranking | `python py/main.py ranking --limite 3` | Retornou os três primeiros do ranking de engajamento. |
| JSON | `python py/main.py top-seguidos 2 --json` | Saída foi aceita pelo conversor JSON do PowerShell. |
| Usuário inexistente | `python py/main.py buscar '@nao_existe'` | Mensagem clara e status 1. |
| Datas invertidas | `python py/main.py posts-entre 2025-09-02 2025-09-01` | Mensagem de erro e status 1. |

