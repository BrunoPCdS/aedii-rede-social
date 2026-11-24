# padrão aedlib 2.6
"""[SOCIAL-26] Montagem dos índices e operações de consulta da rede social."""

from .estruturas import (
    ArvoreAVLSocial,
    GrafoSocial,
    MonteSocial,
    OrdenadorSocial,
    TabelaDispersaSocial,
)


class AplicacaoRedeSocial:
    """[SOCIAL-26] Coordena estruturas próprias e consultas sobre os CSVs."""

    def __init__(self, usuarios, conexoes, posts):
        """[SOCIAL-26] Indexa registros uma vez para reutilizar nas consultas."""
        self.usuarios = usuarios
        self.conexoes = conexoes
        self.posts = posts
        self.tabela_usuarios = TabelaDispersaSocial()
        self.tabela_ids = TabelaDispersaSocial()
        ids = []
        self.posts_por_usuario = [0] * len(usuarios)
        self.curtidas_por_usuario = [0] * len(usuarios)
        self.indice_por_id = TabelaDispersaSocial()

        for indice, usuario in enumerate(usuarios):
            id_usuario = int(usuario[0])
            ids.append(id_usuario)
            self.tabela_usuarios.social_inserir(usuario[1], usuario)
            self.tabela_ids.social_inserir(id_usuario, usuario)
            self.indice_por_id.social_inserir(id_usuario, indice)

        self.grafo = GrafoSocial(ids)
        for conexao in conexoes:
            indice_seguidor = self.indice_por_id.social_buscar(int(conexao[0]))
            indice_seguido = self.indice_por_id.social_buscar(int(conexao[1]))
            if indice_seguidor is not None and indice_seguido is not None:
                self.grafo.social_adicionar_conexao(indice_seguidor, indice_seguido)

        self.arvore_posts = ArvoreAVLSocial()
        for post in posts:
            indice = self.indice_por_id.social_buscar(int(post[1]))
            if indice is not None:
                self.posts_por_usuario[indice] += 1
                self.curtidas_por_usuario[indice] += int(post[3])
            self.arvore_posts.raiz = self.arvore_posts.social_inserir(
                self.arvore_posts.raiz, post[2], post
            )

    def social_buscar(self, nome_usuario):
        """[SOCIAL-26] Retorna perfil e contagens; custo O(V + E + P) nesta versão."""
        usuario = self.tabela_usuarios.social_buscar(nome_usuario)
        if usuario is None:
            return None
        indice = self.indice_por_id.social_buscar(int(usuario[0]))
        return [
            usuario[1], usuario[2], usuario[3],
            len(self.grafo.saidas[indice]),
            self.grafo.total_seguidores[indice],
            self.posts_por_usuario[indice],
        ]

    def social_sugerir(self, nome_usuario, limite):
        """[SOCIAL-26] Retorna sugestões [@usuario, conexões em comum]."""
        usuario = self.tabela_usuarios.social_buscar(nome_usuario)
        if usuario is None:
            raise ValueError("Usuário não encontrado: " + nome_usuario)
        indice = self.indice_por_id.social_buscar(int(usuario[0]))
        itens = self.grafo.social_sugerir(indice, limite)
        resultado = []
        for indice_candidato, pontuacao in itens:
            registro = self.usuarios[indice_candidato]
            resultado.append([registro[1], registro[2], pontuacao])
        return resultado

    def social_comunidades(self):
        """[SOCIAL-26] Retorna [quantidade, tamanhos decrescentes, isolados]."""
        tamanhos, isolados = self.grafo.social_comunidades()
        return [len(tamanhos), tamanhos, isolados]

    def social_posts_entre(self, inicio, fim):
        """[SOCIAL-26] Retorna posts inclusivos entre datas ISO em ordem cronológica."""
        if inicio > fim:
            raise ValueError("A data inicial deve ser menor ou igual à final.")
        resultado = []
        self.arvore_posts.social_buscar_intervalo(self.arvore_posts.raiz, inicio, fim, resultado)
        return resultado

    def social_top_seguidos(self, limite):
        """[SOCIAL-26] Retorna até limite usuários com maior número de seguidores."""
        heap = MonteSocial()
        for indice, usuario in enumerate(self.usuarios):
            heap.social_inserir(self.grafo.total_seguidores[indice], usuario)
        resultado = []
        while len(resultado) < limite and heap.itens:
            entrada = heap.social_remover_maximo()
            usuario = entrada[1]
            resultado.append([usuario[1], usuario[2], entrada[0]])
        return resultado

    def social_top_curtidos(self, limite):
        """[SOCIAL-26] Retorna até limite posts com mais curtidas."""
        heap = MonteSocial()
        for post in self.posts:
            heap.social_inserir(int(post[3]), post)
        resultado = []
        while len(resultado) < limite and heap.itens:
            post = heap.social_remover_maximo()[1]
            autor = self.tabela_ids.social_buscar(int(post[1]))
            nome_autor = autor[1] if autor is not None else "desconhecido"
            resultado.append([post[0], nome_autor, post[2], int(post[3]), post[4]])
        return resultado

    def social_ranking(self, limite=20):
        """[SOCIAL-26] Ordena engajamento desc. e @usuario asc. por Merge Sort."""
        ranking = []
        for indice, usuario in enumerate(self.usuarios):
            engajamento = self.grafo.total_seguidores[indice] * 2 + self.curtidas_por_usuario[indice]
            ranking.append([engajamento, usuario[1], usuario[2]])
        ranking = OrdenadorSocial().social_merge_sort(
            ranking, chave=lambda item: (-item[0], item[1])
        )
        return ranking[:limite]

    def social_total_seguidos(self, nome_usuario):
        """[SOCIAL-26] Retorna quantas contas o usuário segue."""
        registro = self.tabela_usuarios.social_buscar(nome_usuario)
        if registro is None:
            raise ValueError("Usuário não encontrado: " + nome_usuario)
        indice = self.indice_por_id.social_buscar(int(registro[0]))
        return len(self.grafo.saidas[indice])
