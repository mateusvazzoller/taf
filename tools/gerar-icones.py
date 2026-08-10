"""Gera os ícones do app a partir das cores definidas no index.html.

    python tools/gerar-icones.py

Requer Pillow. Os arquivos vão para icons/ e devem ser commitados.
O ícone "maskable" sangra até a borda e mantém o conteúdo na zona segura
central, porque o Android recorta o ícone em formatos diferentes por aparelho.
"""

import os
from PIL import Image, ImageDraw, ImageFont

GROUND = (18, 21, 26, 255)     # --ground do tema escuro
ACCENT = (255, 90, 31, 255)    # --accent

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DESTINO = os.path.join(RAIZ, "icons")


def fonte(tamanho):
    for caminho in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"):
        try:
            return ImageFont.truetype(caminho, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def gerar(size, nome, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if maskable:
        d.rectangle([0, 0, size, size], fill=GROUND)
        escala, centro, larg_barra, y_barra = 0.32, 0.45, 0.28, 0.63
    else:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=GROUND)
        escala, centro, larg_barra, y_barra = 0.42, 0.43, 0.38, 0.68

    f = fonte(int(size * escala))
    texto = "TAF"
    bb = d.textbbox((0, 0), texto, font=f)
    d.text(
        ((size - (bb[2] - bb[0])) / 2 - bb[0], size * centro - (bb[3] - bb[1]) / 2 - bb[1]),
        texto, font=f, fill=ACCENT,
    )

    w = int(size * larg_barra)
    h = max(2, int(size * 0.035))
    y = int(size * y_barra)
    d.rounded_rectangle([(size - w) // 2, y, (size + w) // 2, y + h], radius=h // 2, fill=ACCENT)

    caminho = os.path.join(DESTINO, nome)
    img.save(caminho)
    print("gerado:", nome)


if __name__ == "__main__":
    os.makedirs(DESTINO, exist_ok=True)
    gerar(192, "icon-192.png")
    gerar(512, "icon-512.png")
    gerar(512, "icon-maskable-512.png", maskable=True)
    gerar(180, "apple-touch-icon.png")
