"""Stile grafico di La Finanza Secondo Grinny (matplotlib) — v5 "coerente col logo", ottobre 2026.

Identità: i colori neutri vengono dal logo (blu notte della scritta, verde salvia della freccia),
il titolo è in serif come la scritta del logo; i dati restano corallo (Italia) e pervinca (paragone).

Principio: si disegna alla misura a cui il grafico viene LETTO, non a quella del file.
Substack mostra le immagini larghe circa 730 px, LinkedIn e le anteprime circa 550-600 px.
Ogni formato è quindi progettato in "pixel di lettura" (1 pollice = 100 px) e salvato a 2-3x per la nitidezza.
"""
import os
import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D

# --- Colori -----------------------------------------------------------------------------
SFONDO = "#FFFFFF"
INCHIOSTRO = "#17323D"     # blu notte della scritta del logo: titolo, note, nomi principali
SECONDARIO = "#46585E"     # sottotitolo, numeri sugli assi
TENUE = "#6B7B80"          # fonte, nomi del contesto
ASSE = "#46585E"           # assi e tacche
CONTESTO = "#B9C7C0"       # verde salvia scuro: linee e barre di contorno
CONTESTO_PUNTI = "#9DB0A7"
FASCIA = "#E4EBE6"         # verde salvia della freccia del logo: periodi anomali
SERIE = ["#D9534A", "#4F63D6", "#A86A12", "#2E8B57", "#8E3FA3"]  # corallo, pervinca, ocra, verde, prugna
PROTAGONISTA = SERIE[0]; PARAGONE = SERIE[1]

# --- Formati: (larghezza, altezza) in pollici di lettura, dpi di salvataggio -------------
FORMATI = {
    "articolo": (7.3, 4.6, 300),   # Substack/blog: letto a ~730 px, file 2190 x 1380
    "social":   (6.0, 3.15, 200),  # copertina Substack, anteprima link: file 1200 x 630
    "linkedin": (5.4, 6.75, 200),  # post verticale: file 1080 x 1350
}
# margini in pollici: sinistra, destra, alto, basso
MARGINI = {
    "articolo": (0.55, 1.05, 0.92, 0.82),
    "social":   (0.50, 1.25, 0.90, 0.80),
    "linkedin": (0.55, 1.05, 1.55, 0.90),
}
# corpi in punti, pensati per la misura di lettura
CORPI = {
    "articolo": dict(titolo=16.5, sotto=9.0, assi=8.5, legenda=8.5, nota=8.5, contesto=8.0, piede=7.0, fascia=7.5),
    "social":   dict(titolo=15.5, sotto=8.5, assi=8.5, legenda=8.5, nota=8.5, contesto=8.0, piede=6.5, fascia=7.5),
    "linkedin": dict(titolo=17.0, sotto=9.5, assi=9.0, legenda=9.0, nota=9.0, contesto=8.5, piede=7.5, fascia=8.0),
}
LINEE = dict(protagonista=2.4, paragone=2.0, contesto=1.2)

QUI = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(QUI, "grinny-logo-originale.jpg")  # Drive ID 1tAy3zO9OZSPyEcVvIO0RkuYZs-p1tYbb


def _font_titolo():
    """Serif del titolo: Lora SemiBold. Lora è installata come font variabile, che matplotlib non sa
    rendere in grassetto: la prima volta se ne ricava un'istanza statica (peso 600) accanto al modulo."""
    nome = "Lora Grinny SemiBold"
    file = os.path.join(QUI, "font", "LoraGrinny-SemiBold.ttf")
    if not os.path.exists(file):
        sorgente = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
        if not os.path.exists(sorgente):
            for alt in ("TeX Gyre Pagella", "Caladea", "DejaVu Serif"):   # ripieghi, in ordine
                if alt in {f.name for f in fm.fontManager.ttflist}:
                    return alt
            return "serif"
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        os.makedirs(os.path.dirname(file), exist_ok=True)
        f = instantiateVariableFont(TTFont(sorgente), {"wght": 600})
        for rec in f["name"].names:
            if rec.nameID in (1, 4, 16):
                rec.string = nome
        f.save(file)
    fm.fontManager.addfont(file)
    return nome


def _font():
    disponibili = {f.name for f in fm.fontManager.ttflist}
    for nome in ("Inter", "Source Sans 3", "IBM Plex Sans", "DejaVu Sans"):
        if nome in disponibili:
            return nome
    return "sans-serif"


def applica(formato="articolo"):
    c = CORPI[formato]
    mpl.rcParams.update({
        "font.family": _font(), "font.size": c["assi"],
        "figure.facecolor": SFONDO, "axes.facecolor": SFONDO, "savefig.facecolor": SFONDO,
        "axes.edgecolor": ASSE, "axes.linewidth": 0.7,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.spines.left": True, "axes.spines.bottom": True,
        "axes.grid": False, "axes.axisbelow": True,
        "axes.labelcolor": SECONDARIO, "axes.labelsize": c["assi"],
        "xtick.color": ASSE, "ytick.color": ASSE,
        "xtick.labelcolor": SECONDARIO, "ytick.labelcolor": SECONDARIO,
        "xtick.labelsize": c["assi"], "ytick.labelsize": c["assi"],
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3, "xtick.major.width": 0.7, "ytick.major.width": 0.7,
        "xtick.major.pad": 3, "ytick.major.pad": 3,
        "lines.linewidth": 2.0, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "legend.frameon": True, "legend.edgecolor": ASSE, "legend.fancybox": False,
        "legend.framealpha": 1.0, "legend.fontsize": c["legenda"], "legend.borderpad": 0.5,
        "legend.handlelength": 1.8, "legend.handletextpad": 0.5, "legend.columnspacing": 1.4,
        "legend.labelspacing": 0.35,
        "svg.fonttype": "none",
        "axes.formatter.use_locale": False,
    })


def num(x, dec=1, pct=False, segno=False):
    """Formato italiano: virgola decimale, punto per le migliaia, meno tipografico."""
    s = f"{x:{'+' if segno else ''},.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−") + ("%" if pct else "")


def figura(formato="articolo"):
    applica(formato)
    w, h, dpi = FORMATI[formato]; l, r, t, b = MARGINI[formato]
    fig = plt.figure(figsize=(w, h), dpi=100)
    fig._grinny = formato
    ax = fig.add_axes([l / w, b / h, (w - l - r) / w, (h - t - b) / h])
    return fig, ax


def corpo(fig, chiave):
    return CORPI[getattr(fig, "_grinny", "articolo")][chiave]


def _pollici_y(fig, p):
    """Posizione verticale a p pollici dal bordo alto, in frazione di figura."""
    return 1 - p / fig.get_figheight()


def numeri_italiani(ax, x=True, y=True, dec=None, pct=False):
    """Virgola decimale sui numeri degli assi (matplotlib usa il punto). dec=None: decimali automatici."""
    from matplotlib.ticker import FuncFormatter
    def f(v, _):
        d = dec if dec is not None else (0 if float(v).is_integer() else 1)
        return num(v, d, pct)
    if x: ax.xaxis.set_major_formatter(FuncFormatter(f))
    if y: ax.yaxis.set_major_formatter(FuncFormatter(f))


def assi_stretti(ax, x0, x1, y0, y1):
    """Gli assi finiscono dove finiscono i dati."""
    ax.spines["left"].set_bounds(y0, y1); ax.spines["bottom"].set_bounds(x0, x1)


def intestazione(fig, titolo, sottotitolo):
    """Titolo che dice il fatto, centrato in serif (Lora SemiBold, come la scritta del logo) blu notte,
    sottotitolo centrato in sans. Titolo su due righe con \\n (formato linkedin). Niente occhiello."""
    cx = 0.5
    righe = titolo.count("\n") + 1
    fig.text(cx, _pollici_y(fig, 0.16), titolo, ha="center", va="top", fontsize=corpo(fig, "titolo"),
             fontfamily=_font_titolo(), fontweight="semibold", color=INCHIOSTRO, linespacing=1.1)
    fig.text(cx, _pollici_y(fig, 0.16 + 0.30 * righe + 0.05), sottotitolo, ha="center", va="top",
             fontsize=corpo(fig, "sotto"), color=SECONDARIO, linespacing=1.3)


def legenda(ax, voci, sopra=True, loc="upper left", ncol=None):
    """Solo quando i nomi diretti sono impossibili. voci: lista di (etichetta, colore, spessore).
    sopra=True: su una riga sopra l'area del grafico, così non copre mai i dati."""
    h = [Line2D([0], [0], color=c, lw=w) for _, c, w in voci]
    if sopra:
        leg = ax.legend(h, [e for e, _, _ in voci], loc="lower center", bbox_to_anchor=(0.5, 1.03),
                        ncol=ncol or len(voci), borderaxespad=0)
    else:
        leg = ax.legend(h, [e for e, _, _ in voci], loc=loc, borderaxespad=0.6, ncol=ncol or 1)
    leg.get_frame().set_linewidth(0.6)
    return leg


def nota(ax, x, y, testo, xy=None, ha="left", va="center"):
    """Una frase scritta al posto di staffe e aree colorate. Con xy, una linea sottile e corta la collega al punto."""
    s = corpo(ax.figure, "nota")
    if xy is None:
        ax.text(x, y, testo, ha=ha, va=va, fontsize=s, color=INCHIOSTRO, linespacing=1.3)
    else:
        ax.annotate(testo, xy=xy, xytext=(x, y), ha=ha, va=va, fontsize=s, color=INCHIOSTRO, linespacing=1.3,
                    arrowprops=dict(arrowstyle="-", color=ASSE, lw=0.6, shrinkA=2, shrinkB=3))


def etichetta_fine(ax, x, y, testo, principale=True, dx=0.18):
    """Nome e valore a fine linea. principale=True: blu notte semibold (Italia, paragone);
    False: piccolo e tenue (serie di contesto)."""
    if principale:
        ax.text(x + dx, y, testo, va="center", fontsize=corpo(ax.figure, "nota"), color=INCHIOSTRO,
                fontweight="semibold")
    else:
        ax.text(x + dx, y, testo, va="center", fontsize=corpo(ax.figure, "contesto"), color=TENUE)


def nome_fine_linea(ax, x, y, testo, dx=0.18):
    """Serie di contesto: passare nome e ultimo valore, es. f\"Germania {num(v[-1], 1, True)}\"."""
    etichetta_fine(ax, x, y, testo, principale=False, dx=dx)


def piede(fig, fonte, nota_piede=None):
    ax = fig.axes[0]; x0 = ax.get_position().x0 - 0.35 / fig.get_figwidth()
    righe = fonte if nota_piede is None else fonte + "\n" + nota_piede
    fig.text(max(x0, 0.02), 0.13 / fig.get_figheight(), righe, ha="left", va="bottom",
             fontsize=corpo(fig, "piede"), color=TENUE, linespacing=1.35)
    W, H = fig.get_figwidth(), fig.get_figheight()
    if os.path.exists(LOGO):
        img = mpimg.imread(LOGO)
        alto = 0.40 if getattr(fig, "_grinny", "") != "social" else 0.36    # pollici
        largo = alto * img.shape[1] / img.shape[0]
        lax = fig.add_axes([1 - (largo + 0.12) / W, 0.06 / H, largo / W, alto / H])
        lax.imshow(img); lax.axis("off")
    else:  # solo se manca il file: avvisare l'autore
        fig.text(1 - 0.12 / W, 0.13 / H, "Grinny Finanza", ha="right", va="bottom",
                 fontsize=corpo(fig, "piede"), color=TENUE, fontweight="bold")


def riferimento(ax, x=None, y=None, testo=None):
    """Linea di riferimento tratteggiata scura (soglia, obiettivo), come nei grafici del 2020.
    Chiamarla dopo aver fissato i limiti."""
    s = corpo(ax.figure, "contesto")
    if x is not None:
        ax.axvline(x, color=INCHIOSTRO, lw=1.2, ls=(0, (4, 3)), zorder=5)
        if testo: ax.text(x, ax.get_ylim()[1], " " + testo, ha="left", va="top", fontsize=s, color=INCHIOSTRO)
    if y is not None:
        ax.axhline(y, color=INCHIOSTRO, lw=1.2, ls=(0, (4, 3)), zorder=5)
        if testo: ax.text(ax.get_xlim()[0], y, testo + " ", ha="left", va="bottom", fontsize=s, color=INCHIOSTRO)


def fascia(ax, x0, x1, testo, in_basso=False):
    """Periodo anomalo in salvia, nome in corsivo minuscolo. Chiamarla DOPO aver fissato ylim.
    in_basso=True: nome in fondo alla fascia, quando in alto toccherebbe i dati."""
    ax.axvspan(x0, x1, color=FASCIA, zorder=0, lw=0)
    lo, hi = ax.get_ylim()
    ax.text((x0 + x1) / 2, lo + (hi - lo) * 0.02 if in_basso else hi, testo, ha="center",
            va="bottom" if in_basso else "top",
            fontsize=corpo(ax.figure, "fascia"), color=TENUE, style="italic")


def salva(fig, percorso_senza_estensione):
    dpi = FORMATI[getattr(fig, "_grinny", "articolo")][2]
    fig.savefig(percorso_senza_estensione + ".png", dpi=dpi)
    fig.savefig(percorso_senza_estensione + ".svg")
    plt.close(fig)


# --- Altri tipi di grafico ---------------------------------------------------------------

def barre_orizzontali(ax, etichette, valori, evidenzia=(), paragone=(), dec=1, pct=True, ordina=True, segno=False):
    """Confronto fra Paesi/gruppi. Barre ordinate (la più alta in cima), base a zero (anche con valori negativi).
    Italia in corallo, paragone in pervinca, resto in salvia. Valore scritto a fine barra; asse dei valori tolto."""
    # spazio a sinistra per i nomi: si allarga l'area in base al nome più lungo
    fig = ax.figure; W = fig.get_figwidth(); pos = ax.get_position()
    sinistra = (0.25 + 0.075 * max(len(e) for e in etichette)) / W
    ax.set_position([sinistra, pos.y0, pos.x1 - sinistra, pos.height])
    coppie = sorted(zip(etichette, valori), key=lambda c: c[1]) if ordina else list(zip(etichette, valori))[::-1]
    nomi = [c[0] for c in coppie]; vals = [c[1] for c in coppie]
    colori = [PROTAGONISTA if n in evidenzia else PARAGONE if n in paragone else CONTESTO for n in nomi]
    ax.barh(range(len(vals)), vals, color=colori, height=0.62, edgecolor=SFONDO, linewidth=0.8)
    ax.set_yticks(range(len(vals))); ax.set_yticklabels(nomi)
    for lab, n in zip(ax.get_yticklabels(), nomi):
        if n in evidenzia or n in paragone:
            lab.set_color(INCHIOSTRO); lab.set_fontweight("semibold")
    lo, hi = min(0, min(vals)), max(0, max(vals)); span = hi - lo
    for i, (n, v) in enumerate(zip(nomi, vals)):
        forte = n in evidenzia or n in paragone
        ax.text(v + (span * 0.015 if v >= 0 else -span * 0.015), i, num(v, dec, pct, segno),
                va="center", ha="left" if v >= 0 else "right", fontsize=corpo(ax.figure, "nota"),
                color=INCHIOSTRO if forte else SECONDARIO, fontweight="semibold" if forte else "normal")
    # spazio per le etichette dei valori: almeno ~0,55 pollici oltre la barra più lunga, da entrambi i lati
    largo_in = ax.get_position().width * W; serve = 0.55
    k_dx, k_sx = 0.14, (0.14 if lo < 0 else 0)
    for _ in range(20):
        R = span * (1 + k_dx + k_sx)
        if lo < 0 and span * (k_sx - 0.015) / R * largo_in < serve: k_sx += 0.03
        elif span * (k_dx - 0.015) / R * largo_in < serve: k_dx += 0.03
        else: break
    ax.set_xlim(lo - span * k_sx, hi + span * k_dx)
    ax.spines["bottom"].set_visible(False); ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.tick_params(axis="y", length=0)
    if lo < 0:  # linea dello zero quando ci sono valori negativi
        ax.spines["left"].set_visible(False)
        ax.axvline(0, color=ASSE, lw=0.7, zorder=3)
        ax.tick_params(axis="y", pad=6)


def barre_verticali(ax, etichette, valori, evidenzia=(), dec=1, pct=True):
    """Poche categorie in ordine naturale (anni, fasce d'età, quinti). Base a zero, valore in cima alle barre evidenziate."""
    colori = [PROTAGONISTA if e in evidenzia else PARAGONE for e in etichette]
    ax.bar(range(len(valori)), valori, color=colori, width=0.66, edgecolor=SFONDO, linewidth=0.8)
    ax.set_xticks(range(len(valori))); ax.set_xticklabels(etichette)
    for i, (e, v) in enumerate(zip(etichette, valori)):
        if e in evidenzia:
            ax.annotate(num(v, dec, pct), (i, v), xytext=(0, 3), textcoords="offset points", ha="center",
                        va="bottom", fontsize=corpo(ax.figure, "nota"), color=INCHIOSTRO, fontweight="semibold")


def istogrammi(ax, a, b, bins, nome_a, nome_b):
    """Due distribuzioni sovrapposte, come gli istogrammi Grinny del 2020 ('effettivo' contro 'suggerito')."""
    ax.hist(a, bins=bins, color=SERIE[0], alpha=0.6, edgecolor=SFONDO, linewidth=0.6, label=nome_a, density=True)
    ax.hist(b, bins=bins, color=SERIE[1], alpha=0.6, edgecolor=SFONDO, linewidth=0.6, label=nome_b, density=True)
    leg = ax.legend(loc="upper right", borderaxespad=0.6); leg.get_frame().set_linewidth(0.6)


def punti(ax, x, y, nomi, evidenzia=(), paragone=(), etichetta_tutti=False, retta=False):
    """Relazione fra due grandezze. Punti salvia, Italia in corallo, paragone in pervinca, con il nome.
    retta=True: retta dei minimi quadrati tratteggiata, solo se l'articolo ne parla e mai come prova di causalità."""
    import numpy as np
    for xi, yi, n in zip(x, y, nomi):
        big = n in evidenzia or n in paragone
        col = PROTAGONISTA if n in evidenzia else PARAGONE if n in paragone else CONTESTO_PUNTI
        ax.plot(xi, yi, "o", ms=7 if big else 5.5, color=col, mec=SFONDO, mew=0.8, zorder=4 if big else 3)
        if big or etichetta_tutti:
            ax.annotate(n, (xi, yi), xytext=(5, 3), textcoords="offset points",
                        fontsize=corpo(ax.figure, "nota" if big else "contesto"),
                        color=INCHIOSTRO if big else TENUE, fontweight="semibold" if big else "normal")
    if retta:
        k, q = np.polyfit(x, y, 1); xs = np.array([min(x), max(x)])
        ax.plot(xs, k * xs + q, color=ASSE, lw=0.9, ls=(0, (4, 3)), zorder=2)
