# padrão aedlib 2.6
"""[SOCIAL-26] Ponto de entrada adicional; mantém py/main.py original intacto."""

import sys

from rede_social.cli import social_main


if __name__ == "__main__":
    sys.exit(social_main())
