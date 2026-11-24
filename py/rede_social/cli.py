# padrão aedlib 2.6
"""[SOCIAL-26] Interface de linha de comando para as consultas da rede social."""

import json
import sys
from datetime import date

from aedlib import social_carregar_dados
from .aplicacao import AplicacaoRedeSocial


AJUDA = """Uso: python py/social_main.py COMANDO [ARGUMENTOS] [--json]
Comandos:
  buscar @usuario
  sugerir @usuario k
  comunidades
  posts-entre AAAA-MM-DD AAAA-MM-DD
  top-seguidos k
  top-curtidos k
  ranking [limite]
Exemplos:
  python py/social_main.py buscar @henrique_nascimento
  python py/social_main.py sugerir @henrique_nascimento 5 --json
"""


def social_validar_data(texto):
    """[SOCIAL-26] Valida data ISO e retorna o texto comparável AAAA-MM-DD."""
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        raise ValueError("Data inválida; use AAAA-MM-DD.")
    try:
        date.fromisoformat(texto)
    except ValueError as erro:
        raise ValueError("Data inválida; use AAAA-MM-DD.") from erro
    return texto


def social_inteiro_positivo(texto, nome):
    """[SOCIAL-26] Converte limite não negativo ou gera erro compreensível."""
    try:
        valor = int(texto)
    except ValueError as erro:
        raise ValueError(nome + " deve ser um número inteiro.") from erro
    if valor < 0:
        raise ValueError(nome + " não pode ser negativo.")
    return valor


def social_executar(argumentos):
    """[SOCIAL-26] Valida argumentos e executa uma consulta; retorna dados simples."""
    json_saida = "--json" in argumentos
    argumentos = [item for item in argumentos if item != "--json"]
    if not argumentos or argumentos[0] in ("ajuda", "--help", "-h"):
        print(AJUDA)
        return 0

    usuarios, conexoes, posts = social_carregar_dados()
    app = AplicacaoRedeSocial(usuarios, conexoes, posts)
    comando = argumentos[0].lower()
    parametros = argumentos[1:]

    if comando == "buscar" and len(parametros) == 1:
        resultado = app.social_buscar(parametros[0])
        if resultado is None:
            raise ValueError("Usuário não encontrado: " + parametros[0])
    elif comando == "sugerir" and len(parametros) == 2:
        resultado = app.social_sugerir(parametros[0], social_inteiro_positivo(parametros[1], "k"))
    elif comando == "comunidades" and not parametros:
        resultado = app.social_comunidades()
    elif comando == "posts-entre" and len(parametros) == 2:
        inicio = social_validar_data(parametros[0])
        fim = social_validar_data(parametros[1])
        resultado = app.social_posts_entre(inicio, fim)
    elif comando == "top-seguidos" and len(parametros) == 1:
        resultado = app.social_top_seguidos(social_inteiro_positivo(parametros[0], "k"))
    elif comando == "top-curtidos" and len(parametros) == 1:
        resultado = app.social_top_curtidos(social_inteiro_positivo(parametros[0], "k"))
    elif comando == "ranking" and len(parametros) <= 1:
        limite = social_inteiro_positivo(parametros[0], "limite") if parametros else 20
        resultado = app.social_ranking(limite)
    else:
        print(AJUDA, file=sys.stderr)
        raise ValueError("Comando ou quantidade de parâmetros inválida.")

    if json_saida:
        print(json.dumps(resultado, ensure_ascii=False))
    else:
        print(resultado)
    return 0


def social_main():
    """[SOCIAL-26] Executa a CLI e converte erros de entrada em status 1."""
    try:
        return social_executar(sys.argv[1:])
    except ValueError as erro:
        print("Erro: " + str(erro), file=sys.stderr)
        return 1
