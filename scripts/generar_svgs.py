"""
Generador de las tarjetas SVG ANIMADAS del perfil de GitHub de Miguel Vargas.

Uso (desde la raíz del repo):
    pip install pillow
    python scripts/generar_svgs.py              # tus iniciales "MV" en puntos
    python scripts/generar_svgs.py foto.jpg     # TU foto convertida en puntos

Genera en assets/:
    - perfil-card.svg  -> la terminal animada (se "dibuja" sola al cargar)
    - radar.svg        -> radar de habilidades
    - radar-stack.svg  -> radar de tu stack backend/cloud

Animación de la tarjeta (una sola secuencia de arranque + detalles "en vivo"):
    1. Se escribe el comando en la barra de título.
    2. Los puntos aparecen fila por fila en zigzag (serpentina), como un escáner.
    3. Cada dato del panel derecho se imprime uno tras otro.
    4. "COMPILANDO..." cambia a "BUILD SUCCESSFUL".
    5. Después queda viva: cursor parpadeando, punto ONLINE, línea de escáner y puntos que titilan.

Todo lo editable está en CONFIGURACIÓN.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ============================ CONFIGURACIÓN ============================
USUARIO = "miguelvargas20"          # tu usuario de GitHub (verifícalo)
COMANDO = "miguel@dev:~$ java Perfil.java --live"

INFO = [  # (etiqueta, valor) -> filas del panel derecho
    ("Nombre", "Miguel Vargas"),
    ("Rol", "Full Stack Developer"),
    ("Origen", "Colombia"),
    ("Formación", "Tecnólogo ADSO · SENA"),
    ("Estado", "Aprendiendo + Construyendo"),
    ("Lenguajes", "Java · Python · PHP"),
    ("Frontend", "React · Vite"),
    ("Backend", "Spring Boot · Django · Laravel"),
    ("Bases de datos", "MySQL · MongoDB"),
    ("Cloud", "AWS EC2 · Vercel · Nginx"),
    ("Herramientas", "Git · Maven · VS Code"),
    ("Proyectos", "GoldenBooking · POS"),
    ("LinkedIn", "/in/miguel-andres-vargas-leon"),
    ("Portafolio", "miguelvargas20.github.io"),
]

# Radares: pon números HONESTOS (0-100).
RADAR = ("Radar de habilidades", [
    ("Java", 70), ("React", 65), ("Python", 60),
    ("MySQL", 70), ("PHP", 55), ("MongoDB", 60),
])
RADAR_STACK = ("Backend & Cloud", [
    ("Spring Boot", 70), ("APIs REST", 72), ("WebSocket", 55),
    ("AWS EC2", 50), ("Nginx", 45), ("Git", 70),
])

C = {
    "fondo": "#0d1117",
    "panel": "#111a2b",
    "borde": "#22304a",
    "texto": "#e6edf3",
    "tenue": "#7d8aa3",
    "acento": "#f2a541",     # ámbar café ☕
    "ok": "#3fb950",
    "puntos": "#f2c27b",
}
FUENTE = "ui-monospace, 'Cascadia Code', 'JetBrains Mono', Consolas, monospace"
BANDAS = 26          # filas del escáner en zigzag
VEL_BANDA = 0.09     # segundos entre fila y fila
# ======================================================================

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "assets"
SALIDA.mkdir(exist_ok=True)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fuente(tam):
    try:
        return ImageFont.truetype("DejaVuSansMono-Bold.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def puntos_desde_imagen(img, ancho, alto, max_puntos=7000):
    """Convierte una imagen en una nube de puntos (estilo 1-bit / dithering)."""
    img = ImageOps.autocontrast(ImageOps.fit(ImageOps.grayscale(img), (ancho // 2, alto // 2)))
    px = img.load()
    w, h = img.size
    random.seed(7)
    pts = [(x * 2 + random.uniform(-.4, .4), y * 2 + random.uniform(-.4, .4))
           for y in range(h) for x in range(w)
           if random.random() < (1 - px[x, y] / 255) ** 1.4]
    random.shuffle(pts)
    return pts[:max_puntos]


def imagen_iniciales(ancho, alto):
    img = Image.new("L", (ancho, alto), 255)
    d = ImageDraw.Draw(img)
    f = fuente(int(alto * .40))
    caja = d.textbbox((0, 0), "MV", font=f)
    d.text(((ancho - (caja[2] - caja[0])) / 2 - caja[0], alto * .26 - caja[1]), "MV", font=f, fill=0)
    f2 = fuente(36)
    caja = d.textbbox((0, 0), "</>", font=f2)
    d.text(((ancho - (caja[2] - caja[0])) / 2 - caja[0], alto * .66), "</>", font=f2, fill=0)
    return img


def tarjeta_perfil(foto=None):
    W = 860
    px_, py_, pw = 24, 64, 290
    fila = 22
    ph = 64 + len(INFO) * fila + 34
    H = py_ + ph + 24
    dx, dw = px_ + pw + 16, W - (px_ + pw + 16) - 24
    iw, ih = pw - 40, ph - 70  # área de la imagen

    img = Image.open(foto) if foto else imagen_iniciales(iw, ih)
    pts = puntos_desde_imagen(img, iw, ih)

    # --- 2. puntos por bandas, revelados en zigzag ---
    alto_banda = ih / BANDAS
    bandas = [[] for _ in range(BANDAS)]
    for x, y in pts:
        bandas[min(int(y // alto_banda), BANDAS - 1)].append((x, y))
    inicio_puntos = 0.9
    defs, grupos = [], []
    for i, b in enumerate(bandas):
        t = inicio_puntos + i * VEL_BANDA
        y = i * alto_banda - 1
        if i % 2 == 0:   # izquierda -> derecha
            anim = f'<animate attributeName="width" from="0" to="{iw+4}" begin="{t:.2f}s" dur="{VEL_BANDA*1.6:.2f}s" fill="freeze"/>'
            rect = f'<rect x="-2" y="{y:.1f}" width="0" height="{alto_banda+2:.1f}">{anim}</rect>'
        else:            # derecha -> izquierda
            anim = (f'<animate attributeName="x" from="{iw+2}" to="-2" begin="{t:.2f}s" dur="{VEL_BANDA*1.6:.2f}s" fill="freeze"/>'
                    f'<animate attributeName="width" from="0" to="{iw+4}" begin="{t:.2f}s" dur="{VEL_BANDA*1.6:.2f}s" fill="freeze"/>')
            rect = f'<rect x="{iw+2}" y="{y:.1f}" width="0" height="{alto_banda+2:.1f}">{anim}</rect>'
        defs.append(f'<clipPath id="b{i}">{rect}</clipPath>')
        circ = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r=".9"/>' for x, y in b)
        grupos.append(f'<g clip-path="url(#b{i})">{circ}</g>')
    fin_puntos = inicio_puntos + BANDAS * VEL_BANDA

    # puntos que titilan (detalle "en vivo")
    random.seed(3)
    titilan = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{C["acento"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0" dur="{random.uniform(1.5,3.5):.1f}s" '
        f'begin="{fin_puntos + random.uniform(0,3):.1f}s" repeatCount="indefinite"/></circle>'
        for x, y in random.sample(pts, min(45, len(pts))))

    # --- 3. filas que se imprimen una tras otra ---
    inicio_filas = 1.2
    filas = []
    for i, (k, v) in enumerate(INFO):
        y = py_ + 64 + i * fila
        d = inicio_filas + i * 0.2
        filas.append(
            f'<g class="fila" style="animation-delay:{d:.2f}s">'
            f'<text x="{dx+16}" y="{y}" class="k">{esc(k)}</text>'
            f'<line x1="{dx+130}" y1="{y-4}" x2="{dx+dw-24-len(v)*7.4:.0f}" y2="{y-4}" class="dots"/>'
            f'<text x="{dx+dw-16}" y="{y}" class="v" text-anchor="end">{esc(v)}</text></g>')
    fin_filas = inicio_filas + len(INFO) * 0.2 + 0.3
    fin = max(fin_filas, fin_puntos)

    largo_cmd = len(COMANDO) * 6.1 + 4
    x_cmd = W / 2 - largo_cmd / 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: {FUENTE}; }}
  .k {{ fill: {C["tenue"]}; font-size: 12px; }}
  .v {{ fill: {C["texto"]}; font-size: 12.5px; font-weight: 600; }}
  .t {{ fill: {C["acento"]}; font-size: 12px; font-weight: 700; letter-spacing: 1px; }}
  .s {{ fill: {C["tenue"]}; font-size: 10px; }}
  .dots {{ stroke: {C["borde"]}; stroke-dasharray: 1 4; }}
  .fila {{ opacity: 0; animation: imprimir .35s ease-out forwards; }}
  .cursor {{ animation: blink 1.1s steps(1) infinite; }}
  .vivo {{ animation: pulso 2s ease-in-out infinite; }}
  .compilando {{ animation: salir .2s {fin:.2f}s forwards; }}
  .listo {{ opacity: 0; animation: entrar .4s {fin:.2f}s forwards; }}
  @keyframes imprimir {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes pulso {{ 50% {{ opacity: .25; }} }}
  @keyframes salir {{ to {{ opacity: 0; }} }}
  @keyframes entrar {{ to {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .fila, .listo {{ animation: none; opacity: 1; }}
    .compilando {{ display: none; }}
    .cursor, .vivo {{ animation: none; }}
  }}
</style>
<defs>
  {''.join(defs)}
  <clipPath id="cmd"><rect x="{x_cmd:.0f}" y="14" width="0" height="20">
    <animate attributeName="width" from="0" to="{largo_cmd:.0f}" begin="0.2s" dur="0.7s" fill="freeze"/></rect></clipPath>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{C["acento"]}" stop-opacity="0"/>
    <stop offset="1" stop-color="{C["acento"]}" stop-opacity=".22"/>
  </linearGradient>
  <clipPath id="areaimg"><rect x="0" y="0" width="{iw}" height="{ih}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="12" fill="{C["fondo"]}" stroke="{C["borde"]}"/>
<circle cx="24" cy="24" r="6" fill="#ff5f57"/><circle cx="44" cy="24" r="6" fill="#febc2e"/><circle cx="64" cy="24" r="6" fill="#28c840"/>
<text x="{x_cmd:.0f}" y="28" class="s" clip-path="url(#cmd)">{esc(COMANDO)}</text>
<rect x="{x_cmd+largo_cmd+2:.0f}" y="19" width="7" height="12" fill="{C["acento"]}" class="cursor"/>
<line x1="0" y1="46" x2="{W}" y2="46" stroke="{C["borde"]}"/>

<!-- Panel izquierdo -->
<rect x="{px_}" y="{py_}" width="{pw}" height="{ph}" rx="6" fill="{C["panel"]}" stroke="{C["borde"]}"/>
<text x="{px_+14}" y="{py_+22}" class="t">VISUAL.MAP</text>
<text x="{px_+pw-14}" y="{py_+22}" class="s" text-anchor="end">{pw-40}×{ph-70} / 1-BIT</text>
<path d="M{px_+12} {py_+46} v-10 h10 M{px_+pw-22} {py_+36} h10 v10 M{px_+12} {py_+ph-36} v10 h10 M{px_+pw-22} {py_+ph-26} h10 v-10"
      stroke="{C["tenue"]}" fill="none"/>
<g transform="translate({px_+20},{py_+40})">
  <g fill="{C["puntos"]}">{''.join(grupos)}</g>
  {titilan}
  <g clip-path="url(#areaimg)">
    <rect x="0" y="-40" width="{iw}" height="40" fill="url(#scan)">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="0 {ih+40}"
        begin="{fin_puntos:.1f}s" dur="3.5s" repeatCount="indefinite"/>
    </rect>
  </g>
</g>
<text x="{px_+14}" y="{py_+ph-12}" class="s">PTS {len(pts)} · SCAN/ZIGZAG</text>

<!-- Panel derecho -->
<rect x="{dx}" y="{py_}" width="{dw}" height="{ph}" rx="6" fill="{C["panel"]}" stroke="{C["borde"]}"/>
<text x="{dx+16}" y="{py_+22}" class="t">SYSTEM.INFO</text>
<circle cx="{dx+128}" cy="{py_+18}" r="4" fill="{C["ok"]}" class="vivo"/>
<text x="{dx+138}" y="{py_+22}" class="s" style="fill:{C["ok"]}">ONLINE</text>
<text x="{dx+dw-16}" y="{py_+22}" class="v" text-anchor="end" style="fill:{C["acento"]}">@{USUARIO}</text>
<line x1="{dx}" y1="{py_+34}" x2="{dx+dw}" y2="{py_+34}" stroke="{C["borde"]}"/>
{''.join(filas)}
<line x1="{dx}" y1="{py_+ph-30}" x2="{dx+dw}" y2="{py_+ph-30}" stroke="{C["borde"]}"/>
<text x="{dx+16}" y="{py_+ph-12}" class="s compilando" style="fill:{C["acento"]}">● COMPILANDO...</text>
<text x="{dx+16}" y="{py_+ph-12}" class="s listo" style="fill:{C["ok"]}">● BUILD SUCCESSFUL</text>
<text x="{dx+dw-16}" y="{py_+ph-12}" class="s" text-anchor="end">UTC-5 · COLOMBIA</text>
</svg>'''
    (SALIDA / "perfil-card.svg").write_text(svg, encoding="utf-8")


def radar(titulo, datos, archivo):
    W, H, cx, cy, R = 420, 390, 210, 215, 115
    n = len(datos)
    ang = lambda i: -math.pi / 2 + 2 * math.pi * i / n
    p = lambda i, r: (cx + r * math.cos(ang(i)), cy + r * math.sin(ang(i)))

    rejilla = "".join(
        f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in (p(i, R*k) for i in range(n)))}" fill="none" stroke="{C["borde"]}"/>'
        for k in (.25, .5, .75, 1))
    ejes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{p(i,R)[0]:.1f}" y2="{p(i,R)[1]:.1f}" stroke="{C["borde"]}"/>' for i in range(n))
    forma = " ".join(f"{x:.1f},{y:.1f}" for x, y in (p(i, R * v / 100) for i, (_, v) in enumerate(datos)))
    nodos = "".join(f'<circle cx="{p(i,R*v/100)[0]:.1f}" cy="{p(i,R*v/100)[1]:.1f}" r="3.5" fill="{C["acento"]}"/>'
                    for i, (_, v) in enumerate(datos))
    etq = ""
    for i, (nom, v) in enumerate(datos):
        x, y = p(i, R + 26)
        anc = "middle" if abs(x - cx) < 10 else ("start" if x > cx else "end")
        etq += (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" class="l">{esc(nom)}</text>'
                f'<text x="{x:.1f}" y="{y+13:.1f}" text-anchor="{anc}" class="n">{v}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: {FUENTE}; }}
  .l {{ fill: {C["texto"]}; font-size: 12px; font-weight: 600; }}
  .n {{ fill: {C["acento"]}; font-size: 10.5px; }}
  .forma {{ transform-origin: {cx}px {cy}px; animation: crecer 1.2s ease-out both; }}
  @keyframes crecer {{ from {{ transform: scale(0); opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .forma {{ animation: none; }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="{C["fondo"]}" stroke="{C["borde"]}"/>
<text x="{cx}" y="30" text-anchor="middle" class="l" style="font-size:14px">{esc(titulo)}</text>
{rejilla}{ejes}
<g class="forma"><polygon points="{forma}" fill="{C["acento"]}" fill-opacity=".18" stroke="{C["acento"]}" stroke-width="2"/>{nodos}</g>
{etq}
</svg>'''
    (SALIDA / archivo).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    tarjeta_perfil(sys.argv[1] if len(sys.argv) > 1 else None)
    radar(*RADAR, "radar.svg")
    radar(*RADAR_STACK, "radar-stack.svg")
    print("Listo: assets/perfil-card.svg, assets/radar.svg, assets/radar-stack.svg")
