"""Montagem dos índices e operações de consulta da rede social."""

from .estruturas import (
    ArvoreAVLDePosts,
    GrafoSeguidores,
    HeapMaxima,
    OrdenadorMergeSort,
    TabelaHash,
)


class AplicacaoRedeSocial:
    """Coordena estruturas próprias e consultas sobre os CSVs."""

    def __init__(self, usuarios, conexoes, posts):
        """Indexa registros uma vez para reutilizar nas consultas."""
        self.usuarios = usuarios
        self.conexoes = conexoes
        self.posts = posts
        self.tabela_usuarios = TabelaHash()
        self.tabela_ids = TabelaHash()
        ids = []
        self.posts_por_usuario = [0] * len(usuarios)
        self.curtidas_por_usuario = [0] * len(usuarios)
        self.indice_por_id = TabelaHash()

        for indice, usuario in enumerate(usuarios):
            id_usuario = int(usuario[0])
            ids.append(id_usuario)
            self.tabela_usuarios.inserir(usuario[1], usuario)
            self.tabela_ids.inserir(id_usuario, usuario)
            self.indice_por_id.inserir(id_usuario, indice)

        self.grafo = GrafoSeguidores(ids)
        for conexao in conexoes:
            indice_seguidor = self.indice_por_id.buscar(int(conexao[0]))
            indice_seguido = self.indice_por_id.buscar(int(conexao[1]))
            if indice_seguidor is not None and indice_seguido is not None:
                self.grafo.adicionar_conexao(indice_seguidor, indice_seguido)

        self.arvore_posts = ArvoreAVLDePosts()
        for post in posts:
            indice = self.indice_por_id.buscar(int(post[1]))
            if indice is not None:
                self.posts_por_usuario[indice] += 1
                self.curtidas_por_usuario[indice] += int(post[3])
            self.arvore_posts.raiz = self.arvore_posts.inserir(
                self.arvore_posts.raiz, post[2], post
            )

    def buscar_usuario(self, nome_usuario):
        """Retorna perfil e contagens em tempo médio constante após a carga."""
        usuario = self.tabela_usuarios.buscar(nome_usuario)
        if usuario is None:
            return None
        indice = self.indice_por_id.buscar(int(usuario[0]))
        return [
            usuario[1], usuario[2], usuario[3],
            len(self.grafo.seguidos_por_usuario[indice]),
            self.grafo.quantidade_seguidores[indice],
            self.posts_por_usuario[indice],
        ]

    def sugerir_usuarios(self, nome_usuario, limite):
        """Retorna sugestões [@usuario, conexões em comum]."""
        usuario = self.tabela_usuarios.buscar(nome_usuario)
        if usuario is None:
            raise ValueError("Usuário não encontrado: " + nome_usuario)
        indice = self.indice_por_id.buscar(int(usuario[0]))
        itens = self.grafo.sugerir(indice, limite)
        resultado = []
        for indice_candidato, pontuacao in itens:
            registro = self.usuarios[indice_candidato]
            resultado.append([registro[1], registro[2], pontuacao])
        return resultado

    def listar_comunidades(self):
        """Retorna [quantidade, tamanhos decrescentes, isolados]."""
        tamanhos, isolados = self.grafo.encontrar_comunidades()
        return [len(tamanhos), tamanhos, isolados]

    def buscar_posts_por_periodo(self, inicio, fim):
        """Retorna posts inclusivos entre datas ISO em ordem cronológica."""
        if inicio > fim:
            raise ValueError("A data inicial deve ser menor ou igual à final.")
        resultado = []
        self.arvore_posts.buscar_intervalo(self.arvore_posts.raiz, inicio, fim, resultado)
        return [len(resultado), resultado]

    def listar_mais_seguidos(self, limite):
        """Retorna até limite usuários com maior número de seguidores."""
        heap = HeapMaxima()
        for indice, usuario in enumerate(self.usuarios):
            heap.inserir(self.grafo.quantidade_seguidores[indice], usuario)
        resultado = []
        while len(resultado) < limite and heap.itens:
            entrada = heap.remover_maximo()
            usuario = entrada[1]
            resultado.append([usuario[1], usuario[2], entrada[0]])
        return resultado

    def listar_posts_mais_curtidos(self, limite):
        """Retorna até limite posts com mais curtidas."""
        heap = HeapMaxima()
        for post in self.posts:
            heap.inserir(int(post[3]), post)
        resultado = []
        while len(resultado) < limite and heap.itens:
            post = heap.remover_maximo()[1]
            autor = self.tabela_ids.buscar(int(post[1]))
            nome_autor = autor[1] if autor is not None else "desconhecido"
            resultado.append([post[0], nome_autor, post[2], int(post[3]), post[4]])
        return resultado

    def gerar_ranking(self, limite=20):
        """Ordena engajamento desc. e @usuario asc. por Merge Sort."""
        ranking = []
        for indice, usuario in enumerate(self.usuarios):
            engajamento = self.grafo.quantidade_seguidores[indice] * 2 + self.curtidas_por_usuario[indice]
            ranking.append([engajamento, usuario[1], usuario[2]])
        ranking = OrdenadorMergeSort().ordenar(
            ranking, chave=lambda item: (-item[0], item[1])
        )
        return ranking[:limite]

    def contar_seguidos(self, nome_usuario):
        """Retorna quantas contas o usuário segue."""
        registro = self.tabela_usuarios.buscar(nome_usuario)
        if registro is None:
            raise ValueError("Usuário não encontrado: " + nome_usuario)
        indice = self.indice_por_id.buscar(int(registro[0]))
        return len(self.grafo.seguidos_por_usuario[indice])
