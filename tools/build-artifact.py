"""Gera a versão do app para publicar como Artifact do Claude.

    python tools/build-artifact.py

Lê o index.html (fonte única da verdade) e escreve dist/artifact.html, que é o
mesmo app sem <!DOCTYPE>, <html>, <head>, <body> e sem o registro do service
worker — o Artifact envolve o conteúdo na própria casca e bloqueia service
worker. Publique dist/artifact.html com a ferramenta Artifact.

Só é necessário se você quiser manter o Artifact antigo atualizado. O canal
oficial hoje é o GitHub Pages, e lá o arquivo publicado é o index.html direto.
"""

import io
import os
import re

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ENTRADA = os.path.join(RAIZ, "index.html")
SAIDA_DIR = os.path.join(RAIZ, "dist")
SAIDA = os.path.join(SAIDA_DIR, "artifact.html")


def main():
    html = io.open(ENTRADA, encoding="utf-8").read()

    corpo = re.search(r"<body>(.*)</body>", html, re.S)
    if not corpo:
        raise SystemExit("Não achei <body> no index.html — o arquivo mudou de forma?")
    corpo = corpo.group(1)

    # o Artifact bloqueia service worker; tira o bloco de registro
    corpo = re.sub(
        r'<script>\s*/\* Guarda o app no aparelho.*?</script>',
        "", corpo, flags=re.S,
    )

    # o <title> vive no index.html dentro do <head>; o Artifact espera no corpo
    titulo = re.search(r"<title>(.*?)</title>", html, re.S)
    if titulo and "<title>" not in corpo:
        corpo = "<title>%s</title>\n" % titulo.group(1) + corpo

    os.makedirs(SAIDA_DIR, exist_ok=True)
    io.open(SAIDA, "w", encoding="utf-8").write(corpo.strip() + "\n")
    print("gerado:", os.path.relpath(SAIDA, RAIZ))


if __name__ == "__main__":
    main()
