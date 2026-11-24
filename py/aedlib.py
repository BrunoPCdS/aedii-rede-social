"""
aedlib - biblioteca base do projeto Rede Social (AED II).

Responsável pela carga padronizada dos dados. Não remova este módulo:
o main depende dele.

"""
import os

_RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def ler_csv(nome):
    """Lê um CSV separado por ponto e vírgula e ignora o cabeçalho."""
    with open(os.path.join(_RAIZ, nome), encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()
    return [linha.split(";") for linha in linhas[1:] if linha]


def carregar_dados():
    """Carrega e devolve os usuários, as conexões e os posts dos arquivos CSV."""
    return (ler_csv("usuarios.csv"),
            ler_csv("seguidores.csv"),
            ler_csv("posts.csv"))
