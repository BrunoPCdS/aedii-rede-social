# padrão aedlib 2.6
"""[SOCIAL-26] Estruturas de dados próprias usadas pela rede social."""


class TabelaDispersaSocial:
    """[SOCIAL-26] Tabela hash com encadeamento separado para colisões."""

    def __init__(self, tamanho=4099):
        """[SOCIAL-26] Inicializa os baldes; tamanho controla a distribuição."""
        self.tamanho = tamanho
        self.baldes = [[] for _ in range(tamanho)]

    def social_hash(self, chave):
        """[SOCIAL-26] Calcula um índice por polinômio em O(comprimento da chave)."""
        texto = str(chave)
        valor = 0
        for caractere in texto:
            valor = (valor * 31 + ord(caractere)) % self.tamanho
        return valor

    def social_inserir(self, chave, valor):
        """[SOCIAL-26] Insere ou substitui a chave; colisões ficam no mesmo balde."""
        balde = self.baldes[self.social_hash(chave)]
        for entrada in balde:
            if entrada[0] == chave:
                entrada[1] = valor
                return
        balde.append([chave, valor])

    def social_buscar(self, chave):
        """[SOCIAL-26] Retorna o valor da chave, ou None se ela não estiver na tabela."""
        for entrada in self.baldes[self.social_hash(chave)]:
            if entrada[0] == chave:
                return entrada[1]
        return None


class MonteSocial:
    """[SOCIAL-26] Heap binária de máximo para pares [prioridade, valor]."""

    def __init__(self):
        """[SOCIAL-26] Cria uma heap vazia representada por lista simples."""
        self.itens = []

    def social_inserir(self, prioridade, valor):
        """[SOCIAL-26] Insere e sobe o item até restaurar a heap, em O(log n)."""
        self.itens.append([prioridade, valor])
        indice = len(self.itens) - 1
        while indice > 0:
            pai = (indice - 1) // 2
            if self.itens[pai][0] >= self.itens[indice][0]:
                break
            self.itens[pai], self.itens[indice] = self.itens[indice], self.itens[pai]
            indice = pai

    def social_remover_maximo(self):
        """[SOCIAL-26] Remove a raiz e reorganiza a heap em O(log n); vazia retorna None."""
        if not self.itens:
            return None
        maior = self.itens[0]
        ultimo = self.itens.pop()
        if self.itens:
            self.itens[0] = ultimo
            indice = 0
            while True:
                esquerda = indice * 2 + 1
                direita = esquerda + 1
                maior_filho = indice
                if esquerda < len(self.itens) and self.itens[esquerda][0] > self.itens[maior_filho][0]:
                    maior_filho = esquerda
                if direita < len(self.itens) and self.itens[direita][0] > self.itens[maior_filho][0]:
                    maior_filho = direita
                if maior_filho == indice:
                    break
                self.itens[indice], self.itens[maior_filho] = self.itens[maior_filho], self.itens[indice]
                indice = maior_filho
        return maior


class GrafoSocial:
    """[SOCIAL-26] Grafo dirigido com adjacências de saída e entrada."""

    def __init__(self, ids_usuarios):
        """[SOCIAL-26] Cria vértices e índices; cada posição corresponde a um usuário."""
        self.ids = list(ids_usuarios)
        quantidade = len(self.ids)
        self.saidas = [[] for _ in range(quantidade)]
        self.entradas = [[] for _ in range(quantidade)]
        self.total_seguidores = [0] * quantidade

    def social_adicionar_conexao(self, seguidor, seguido):
        """[SOCIAL-26] Registra a aresta dirigida e incrementa seguidores do destino."""
        self.saidas[seguidor].append(seguido)
        self.entradas[seguido].append(seguidor)
        self.total_seguidores[seguido] += 1

    def social_sugerir(self, usuario, limite):
        """[SOCIAL-26] Seleciona até limite candidatos por amigos em comum usando heap."""
        quantidade = len(self.ids)
        ja_segue = [False] * quantidade
        pontuacoes = [0] * quantidade
        for seguido in self.saidas[usuario]:
            ja_segue[seguido] = True
        for seguido in self.saidas[usuario]:
            for candidato in self.saidas[seguido]:
                if candidato != usuario and not ja_segue[candidato]:
                    pontuacoes[candidato] += 1
        heap = MonteSocial()
        for candidato in range(quantidade):
            if pontuacoes[candidato] > 0:
                heap.social_inserir(pontuacoes[candidato], candidato)
        resultado = []
        while len(resultado) < limite and heap.itens:
            candidato = heap.social_remover_maximo()
            resultado.append([candidato[1], candidato[0]])
        return resultado

    def social_comunidades(self):
        """[SOCIAL-26] Calcula componentes não dirigidos por BFS em O(V + E)."""
        visitado = [False] * len(self.ids)
        tamanhos = []
        isolados = 0
        for inicio in range(len(self.ids)):
            if visitado[inicio]:
                continue
            fila = [inicio]
            cabeca = 0
            visitado[inicio] = True
            tamanho = 0
            while cabeca < len(fila):
                atual = fila[cabeca]
                cabeca += 1
                tamanho += 1
                for vizinho in self.saidas[atual] + self.entradas[atual]:
                    if not visitado[vizinho]:
                        visitado[vizinho] = True
                        fila.append(vizinho)
            if tamanho == 1 and not self.saidas[inicio] and not self.entradas[inicio]:
                isolados += 1
            tamanhos.append(tamanho)
        tamanhos = OrdenadorSocial().social_merge_sort(tamanhos, decrescente=True)
        return tamanhos, isolados


class NoArvoreSocial:
    """[SOCIAL-26] Nó AVL que agrupa posts publicados na mesma data."""

    def __init__(self, data, post):
        """[SOCIAL-26] Inicializa data, lista de posts, filhos e altura do nó."""
        self.data = data
        self.posts = [post]
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVLSocial:
    """[SOCIAL-26] AVL de datas com consulta de intervalo podada."""

    def __init__(self):
        """[SOCIAL-26] Cria uma árvore sem raiz."""
        self.raiz = None

    def social_altura(self, no):
        """[SOCIAL-26] Retorna a altura do nó; árvore vazia tem altura zero."""
        return no.altura if no is not None else 0

    def social_atualizar_altura(self, no):
        """[SOCIAL-26] Atualiza altura a partir dos filhos em O(1)."""
        no.altura = 1 + max(self.social_altura(no.esquerda), self.social_altura(no.direita))

    def social_rotacao_direita(self, raiz):
        """[SOCIAL-26] Executa rotação simples à direita e atualiza alturas."""
        nova_raiz = raiz.esquerda
        raiz.esquerda = nova_raiz.direita
        nova_raiz.direita = raiz
        self.social_atualizar_altura(raiz)
        self.social_atualizar_altura(nova_raiz)
        return nova_raiz

    def social_rotacao_esquerda(self, raiz):
        """[SOCIAL-26] Executa rotação simples à esquerda e atualiza alturas."""
        nova_raiz = raiz.direita
        raiz.direita = nova_raiz.esquerda
        nova_raiz.esquerda = raiz
        self.social_atualizar_altura(raiz)
        self.social_atualizar_altura(nova_raiz)
        return nova_raiz

    def social_inserir(self, no, data, post):
        """[SOCIAL-26] Insere post por data, rebalanceia e retorna a raiz resultante."""
        if no is None:
            return NoArvoreSocial(data, post)
        if data == no.data:
            no.posts.append(post)
            return no
        if data < no.data:
            no.esquerda = self.social_inserir(no.esquerda, data, post)
        else:
            no.direita = self.social_inserir(no.direita, data, post)
        self.social_atualizar_altura(no)
        fator = self.social_altura(no.esquerda) - self.social_altura(no.direita)
        if fator > 1:
            if data > no.esquerda.data:
                no.esquerda = self.social_rotacao_esquerda(no.esquerda)
            return self.social_rotacao_direita(no)
        if fator < -1:
            if data < no.direita.data:
                no.direita = self.social_rotacao_direita(no.direita)
            return self.social_rotacao_esquerda(no)
        return no

    def social_buscar_intervalo(self, no, inicio, fim, resultado):
        """[SOCIAL-26] Coleta posts inclusivos em ordem cronológica, podando ramos."""
        if no is None:
            return
        if inicio < no.data:
            self.social_buscar_intervalo(no.esquerda, inicio, fim, resultado)
        if inicio <= no.data <= fim:
            for post in no.posts:
                resultado.append(post)
        if no.data < fim:
            self.social_buscar_intervalo(no.direita, inicio, fim, resultado)


class OrdenadorSocial:
    """[SOCIAL-26] Merge Sort próprio para listas e rankings."""

    def social_merge_sort(self, itens, decrescente=False, chave=None):
        """[SOCIAL-26] Ordena em O(n log n), sem sorted ou sort nativo."""
        if len(itens) <= 1:
            return itens[:]
        meio = len(itens) // 2
        esquerda = self.social_merge_sort(itens[:meio], decrescente, chave)
        direita = self.social_merge_sort(itens[meio:], decrescente, chave)
        resultado = []
        i = j = 0
        while i < len(esquerda) and j < len(direita):
            a = chave(esquerda[i]) if chave else esquerda[i]
            b = chave(direita[j]) if chave else direita[j]
            if (a >= b) if decrescente else (a <= b):
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1
        resultado.extend(esquerda[i:])
        resultado.extend(direita[j:])
        return resultado
