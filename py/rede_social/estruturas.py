"""Estruturas de dados próprias usadas pela rede social."""


class TabelaHash:
    """Tabela hash com encadeamento separado para colisões."""

    def __init__(self, tamanho=4099):
        """Inicializa os baldes; tamanho controla a distribuição."""
        self.tamanho = tamanho
        self.baldes = [[] for _ in range(tamanho)]

    def calcular_indice(self, chave):
        """Calcula um índice por polinômio em O(comprimento da chave)."""
        texto = str(chave)
        valor = 0
        for caractere in texto:
            valor = (valor * 31 + ord(caractere)) % self.tamanho
        return valor

    def inserir(self, chave, valor):
        """Insere ou substitui a chave; colisões ficam no mesmo balde."""
        balde = self.baldes[self.calcular_indice(chave)]
        for entrada in balde:
            if entrada[0] == chave:
                entrada[1] = valor
                return
        balde.append([chave, valor])

    def buscar(self, chave):
        """Retorna o valor da chave, ou None se ela não estiver na tabela."""
        for entrada in self.baldes[self.calcular_indice(chave)]:
            if entrada[0] == chave:
                return entrada[1]
        return None


class HeapMaxima:
    """Heap binária de máximo para pares [prioridade, valor]."""

    def __init__(self):
        """Cria uma heap vazia representada por lista simples."""
        self.itens = []

    def inserir(self, prioridade, valor):
        """Insere e sobe o item até restaurar a heap, em O(log n)."""
        self.itens.append([prioridade, valor])
        indice = len(self.itens) - 1
        while indice > 0:
            pai = (indice - 1) // 2
            if self.itens[pai][0] >= self.itens[indice][0]:
                break
            self.itens[pai], self.itens[indice] = self.itens[indice], self.itens[pai]
            indice = pai

    def remover_maximo(self):
        """Remove a raiz e reorganiza a heap em O(log n); vazia retorna None."""
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


class GrafoSeguidores:
    """Grafo dirigido com adjacências de saída e entrada."""

    def __init__(self, ids_usuarios):
        """Cria vértices e índices; cada posição corresponde a um usuário."""
        self.ids = list(ids_usuarios)
        quantidade = len(self.ids)
        self.seguidos_por_usuario = [[] for _ in range(quantidade)]
        self.seguidores_por_usuario = [[] for _ in range(quantidade)]
        self.quantidade_seguidores = [0] * quantidade

    def adicionar_conexao(self, seguidor, seguido):
        """Registra a aresta dirigida e incrementa seguidores do destino."""
        self.seguidos_por_usuario[seguidor].append(seguido)
        self.seguidores_por_usuario[seguido].append(seguidor)
        self.quantidade_seguidores[seguido] += 1

    def sugerir(self, usuario, limite):
        """Seleciona até limite candidatos por amigos em comum usando heap."""
        quantidade = len(self.ids)
        ja_segue = [False] * quantidade
        pontuacoes = [0] * quantidade
        for seguido in self.seguidos_por_usuario[usuario]:
            ja_segue[seguido] = True
        for seguido in self.seguidos_por_usuario[usuario]:
            for candidato in self.seguidos_por_usuario[seguido]:
                if candidato != usuario and not ja_segue[candidato]:
                    pontuacoes[candidato] += 1
        heap = HeapMaxima()
        for candidato in range(quantidade):
            if pontuacoes[candidato] > 0:
                heap.inserir(pontuacoes[candidato], candidato)
        resultado = []
        while len(resultado) < limite and heap.itens:
            candidato = heap.remover_maximo()
            resultado.append([candidato[1], candidato[0]])
        return resultado

    def encontrar_comunidades(self):
        """Calcula componentes não dirigidos por BFS em O(V + E)."""
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
                for vizinho in self.seguidos_por_usuario[atual] + self.seguidores_por_usuario[atual]:
                    if not visitado[vizinho]:
                        visitado[vizinho] = True
                        fila.append(vizinho)
            if tamanho == 1 and not self.seguidos_por_usuario[inicio] and not self.seguidores_por_usuario[inicio]:
                isolados += 1
            tamanhos.append(tamanho)
        tamanhos = OrdenadorMergeSort().ordenar(tamanhos, decrescente=True)
        return tamanhos, isolados


class NoAVLDePosts:
    """Nó AVL que agrupa posts publicados na mesma data."""

    def __init__(self, data, post):
        """Inicializa data, lista de posts, filhos e altura do nó."""
        self.data = data
        self.posts = [post]
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVLDePosts:
    """AVL de datas com consulta de intervalo podada."""

    def __init__(self):
        """Cria uma árvore sem raiz."""
        self.raiz = None

    def altura(self, no):
        """Retorna a altura do nó; árvore vazia tem altura zero."""
        return no.altura if no is not None else 0

    def atualizar_altura(self, no):
        """Atualiza altura a partir dos filhos em O(1)."""
        no.altura = 1 + max(self.altura(no.esquerda), self.altura(no.direita))

    def rotacao_direita(self, raiz):
        """Executa rotação simples à direita e atualiza alturas."""
        nova_raiz = raiz.esquerda
        raiz.esquerda = nova_raiz.direita
        nova_raiz.direita = raiz
        self.atualizar_altura(raiz)
        self.atualizar_altura(nova_raiz)
        return nova_raiz

    def rotacao_esquerda(self, raiz):
        """Executa rotação simples à esquerda e atualiza alturas."""
        nova_raiz = raiz.direita
        raiz.direita = nova_raiz.esquerda
        nova_raiz.esquerda = raiz
        self.atualizar_altura(raiz)
        self.atualizar_altura(nova_raiz)
        return nova_raiz

    def inserir(self, no, data, post):
        """Insere post por data, rebalanceia e retorna a raiz resultante."""
        if no is None:
            return NoAVLDePosts(data, post)
        if data == no.data:
            no.posts.append(post)
            return no
        if data < no.data:
            no.esquerda = self.inserir(no.esquerda, data, post)
        else:
            no.direita = self.inserir(no.direita, data, post)
        self.atualizar_altura(no)
        fator = self.altura(no.esquerda) - self.altura(no.direita)
        if fator > 1:
            if data > no.esquerda.data:
                no.esquerda = self.rotacao_esquerda(no.esquerda)
            return self.rotacao_direita(no)
        if fator < -1:
            if data < no.direita.data:
                no.direita = self.rotacao_direita(no.direita)
            return self.rotacao_esquerda(no)
        return no

    def buscar_intervalo(self, no, inicio, fim, resultado):
        """Coleta posts inclusivos em ordem cronológica, podando ramos."""
        if no is None:
            return
        if inicio < no.data:
            self.buscar_intervalo(no.esquerda, inicio, fim, resultado)
        if inicio <= no.data <= fim:
            for post in no.posts:
                resultado.append(post)
        if no.data < fim:
            self.buscar_intervalo(no.direita, inicio, fim, resultado)


class OrdenadorMergeSort:
    """Merge Sort próprio para listas e rankings."""

    def ordenar(self, itens, decrescente=False, chave=None):
        """Ordena em O(n log n), sem sorted ou sort nativo."""
        if len(itens) <= 1:
            return itens[:]
        meio = len(itens) // 2
        esquerda = self.ordenar(itens[:meio], decrescente, chave)
        direita = self.ordenar(itens[meio:], decrescente, chave)
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
