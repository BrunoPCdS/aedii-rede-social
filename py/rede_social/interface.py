"""Interface de linha de comando para as consultas da rede social."""

import json
import sys
from datetime import date

from aedlib import carregar_dados
from .aplicacao import AplicacaoRedeSocial


AJUDA = """Uso: python py/main.py COMANDO [ARGUMENTOS] [--json]
Comandos:
  buscar @usuario
  sugerir @usuario k
  comunidades
  posts-entre AAAA-MM-DD AAAA-MM-DD
  top-seguidos k
  top-curtidos k
  ranking [--limite N]
Exemplos:
  python py/main.py buscar @henrique_nascimento
  python py/main.py sugerir @henrique_nascimento 5 --json
  python py/main.py ranking --limite 20
"""


def validar_data(texto):
    """Valida data ISO e retorna o texto comparável AAAA-MM-DD."""
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        raise ValueError("Data inválida; use AAAA-MM-DD.")
    try:
        date.fromisoformat(texto)
    except ValueError as erro:
        raise ValueError("Data inválida; use AAAA-MM-DD.") from erro
    return texto


def converter_inteiro(texto, nome):
    """Converte limite não negativo ou gera erro compreensível."""
    try:
        valor = int(texto)
    except ValueError as erro:
        raise ValueError(nome + " deve ser um número inteiro.") from erro
    if valor < 0:
        raise ValueError(nome + " não pode ser negativo.")
    return valor


def executar_comando(argumentos):
    """Valida argumentos e executa uma consulta; retorna dados simples."""
    json_saida = "--json" in argumentos
    argumentos = [item for item in argumentos if item != "--json"]
    if not argumentos or argumentos[0] in ("ajuda", "--help", "-h"):
        print(AJUDA)
        return 0

    usuarios, conexoes, posts = carregar_dados()
    app = AplicacaoRedeSocial(usuarios, conexoes, posts)
    comando = argumentos[0].lower()
    parametros = argumentos[1:]

    if comando == "buscar" and len(parametros) == 1:
        resultado = app.buscar_usuario(parametros[0])
        if resultado is None:
            raise ValueError("Usuário não encontrado: " + parametros[0])
    elif comando == "sugerir" and len(parametros) == 2:
        resultado = app.sugerir_usuarios(parametros[0], converter_inteiro(parametros[1], "k"))
    elif comando == "comunidades" and not parametros:
        resultado = app.listar_comunidades()
    elif comando == "posts-entre" and len(parametros) == 2:
        inicio = validar_data(parametros[0])
        fim = validar_data(parametros[1])
        resultado = app.buscar_posts_por_periodo(inicio, fim)
    elif comando == "top-seguidos" and len(parametros) == 1:
        resultado = app.listar_mais_seguidos(converter_inteiro(parametros[0], "k"))
    elif comando == "top-curtidos" and len(parametros) == 1:
        resultado = app.listar_posts_mais_curtidos(converter_inteiro(parametros[0], "k"))
    elif comando == "ranking":
        if not parametros:
            limite = 20
        elif len(parametros) == 2 and parametros[0] == "--limite":
            limite = converter_inteiro(parametros[1], "limite")
        elif len(parametros) == 1:
            limite = converter_inteiro(parametros[0], "limite")
        else:
            print(AJUDA, file=sys.stderr)
            raise ValueError("Use ranking ou ranking --limite N.")
        resultado = app.gerar_ranking(limite)
    else:
        print(AJUDA, file=sys.stderr)
        raise ValueError("Comando ou quantidade de parâmetros inválida.")

    if json_saida:
        print(json.dumps(resultado, ensure_ascii=False))
    else:
        print(resultado)
    return 0


def iniciar_interface():
    """Executa a CLI e converte erros de entrada em status 1."""
    try:
        return executar_comando(sys.argv[1:])
    except ValueError as erro:
        print("Erro: " + str(erro), file=sys.stderr)
        return 1
