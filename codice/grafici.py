"""Grafici del pezzo sul cuscinetto di rendimento (stile Grinny, tre formati ciascuno).

Uso:  python codice/grafici.py   (dopo codice/analisi.py)
Ogni numero scritto nei grafici è ricalcolato dai CSV in risultati/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grinny_style as g  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
RIS = BASE / "risultati"
OUT = BASE / "grafici"
OUT.mkdir(exist_ok=True)
S = json.loads((RIS / "sintesi.json").read_text())
ESTRAZIONE = "25/10/2026"

tab = pd.read_csv(RIS / "soglie_giornaliere.csv", parse_dates=["data"]).set_index("data")


def data_it(ts):
    return pd.Timestamp(ts).strftime("%d/%m/%Y")


# --------------------------------------------------------------------------------------
# 1. Rendimento del BTP decennale e soglia di perdita un anno dopo, con i collegamenti
#    (alla maniera di FT Alphaville: ogni linea grigia va dal rendimento di un giorno alla sua soglia)
# --------------------------------------------------------------------------------------
INIZIO_SOGLIA = "2009-01-01"


def episodi_perdita(df, minimo=20):
    """Intervalli di date d'acquisto consecutive con perdita a un anno (esito noto)."""
    p = df.dropna(subset=["y1"])["perdita"].astype(bool)
    gruppi = (p != p.shift()).cumsum()
    return [(x.index.min(), x.index.max()) for _, x in p[p].groupby(gruppi[p]) if len(x) >= minimo]


def grafico_soglia(formato):
    d = tab[tab.serie == "BTP 10 anni"]
    ultimo = d.dropna(subset=["y0"]).iloc[-1]; t_u = d.dropna(subset=["y0"]).index[-1]
    assert round(float(ultimo.soglia), 2) == S["serie"]["BTP 10 anni"]["soglia_esatta"]
    assert g.num(ultimo.soglia, 1, True) == "5,2%"  # la risposta, scritta sul grafico

    # titolo a domanda scelto dall'autore (29/10/2026): su due righe in tutti i formati
    fig, ax = g.figura(formato, spazio_titolo=0.30 if formato != "linkedin" else 0.0)
    x0, x1 = pd.Timestamp(INIZIO_SOGLIA), pd.Timestamp("2027-12-31")
    ymax = 9
    ax.set_xlim(x0, x1); ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1, 1 if formato == "articolo" else 2)); g.numeri_italiani(ax, x=False, pct=True, dec=0)
    anni = range(2009, 2028)
    passo = 2 if formato == "articolo" else 4
    ax.set_xticks([pd.Timestamp(f"{a}-01-01") for a in anni])
    ax.set_xticklabels([str(a) if (a - 2009) % passo == 0 or a == 2027 else "" for a in anni])
    g.assi_stretti(ax, mdates.date2num(x0), mdates.date2num(x1), 0, ymax)

    # fasce: date d'acquisto da cui si è perso a un anno
    for a, b in episodi_perdita(d.loc[INIZIO_SOGLIA:]):
        ax.axvspan(a, b, color=g.FASCIA, zorder=0, lw=0)

    sett = d.loc[INIZIO_SOGLIA:].resample("W-FRI").last().dropna(subset=["y0"])
    # un collegamento per ogni punto blu: dal rendimento della settimana d'acquisto alla sua soglia un anno dopo
    for t, r in sett.iterrows():
        ax.plot([t, t + pd.Timedelta(days=365)], [r.y0, r.soglia], color=g.CONTESTO, lw=0.3, alpha=0.5, zorder=1)
    ax.plot(sett.index + pd.Timedelta(days=365), sett.soglia, "o", ms=1.5, color=g.PARAGONE, zorder=3)
    ax.plot(sett.index, sett.y0, color=g.PROTAGONISTA, lw=g.LINEE["protagonista"], zorder=4)
    ax.plot([t_u], [ultimo.y0], "o", color=g.PROTAGONISTA, ms=4.5, zorder=5)
    ax.plot([t_u + pd.Timedelta(days=365)], [ultimo.soglia], "o", color=g.PARAGONE, ms=4.5, zorder=5)

    a_capo = "\n" if formato != "articolo" else " "
    ax.annotate(f"Rendimento{a_capo}{g.num(ultimo.y0, 2, True)}", xy=(t_u, ultimo.y0),
                xytext=(t_u - pd.Timedelta(days=420), 7.6), ha="right", va="bottom",
                fontsize=g.corpo(fig, "nota"), color=g.INCHIOSTRO, fontweight="semibold",
                arrowprops=dict(arrowstyle="-", color=g.ASSE, lw=0.6, shrinkA=2, shrinkB=4))
    ax.text(t_u + pd.Timedelta(days=395), ultimo.soglia + 0.45, f"Soglia\n{g.num(ultimo.soglia, 2, True)}",
            fontsize=g.corpo(fig, "nota"), color=g.INCHIOSTRO, fontweight="semibold", ha="right", va="bottom")
    if formato != "social":
        if formato == "articolo":
            g.nota(ax, pd.Timestamp("2014-08-01"), 8.6,
                   "Ogni linea collega il rendimento iniziale alla soglia\nche, dopo dodici mesi, azzererebbe il rendimento totale")
        else:
            g.nota(ax, pd.Timestamp("2014-06-01"), 8.2, "Ogni linea collega\nil rendimento iniziale\nalla soglia a 12 mesi")

    titolo = "Quanto devono salire i rendimenti\nperché il BTP chiuda l'anno in perdita?"
    sotto = {"articolo": "Rendimento del BTP decennale e soglia di pareggio a dodici mesi, in %",
             "social": "Rendimento del BTP decennale e soglia di pareggio a dodici mesi, in %",
             "linkedin": "Rendimento del BTP decennale\ne soglia di pareggio a dodici mesi, in %"}[formato]
    g.intestazione(fig, titolo, sotto)
    fonte = {"articolo": f"Fonte: elaborazione Grinny Finanza su dati Banca d'Italia, BDS, tavola BMK0200, estratti il {ESTRAZIONE}.",
             "social": f"Fonte: elaborazione Grinny Finanza su dati Banca d'Italia (BMK0200), {ESTRAZIONE}.",
             "linkedin": f"Fonte: elaborazione Grinny Finanza su dati\nBanca d'Italia (BMK0200), estratti il {ESTRAZIONE}."}[formato]
    nota_p = ("Fasce verdi: date d'acquisto che hanno chiuso i dodici mesi successivi in perdita. "
              "BTP sintetico comprato alla pari. Dati al 30/09/2026.") if formato == "articolo" else None
    g.piede(fig, fonte, nota_p)
    g.salva(fig, str(OUT / f"btp10-soglia-perdita_{formato}"))


# --------------------------------------------------------------------------------------
# 2. Margine a un anno, alla stessa data, per BTP e Bund a 3 e 10 anni
# --------------------------------------------------------------------------------------
def grafico_margini(formato):
    c = S["alla_data_comune"]
    nomi = ["BTP 3 anni", "Bund 3 anni", "BTP 10 anni", "Bund 10 anni"]
    valori = [c[n]["margine_pb"] for n in nomi]
    # il fatto del titolo: a tre anni il margine è almeno il triplo che a dieci, per entrambi
    assert c["BTP 3 anni"]["margine_pb"] >= 3 * c["BTP 10 anni"]["margine_pb"]
    assert c["Bund 3 anni"]["margine_pb"] >= 3 * c["Bund 10 anni"]["margine_pb"]
    fig, ax = g.figura(formato)
    g.barre_orizzontali(ax, nomi, valori, evidenzia=["BTP 3 anni", "BTP 10 anni"],
                        paragone=["Bund 3 anni", "Bund 10 anni"], dec=0, pct=False)
    titolo = {"articolo": "Sui titoli a 3 anni il cuscinetto è almeno tre volte più largo",
              "social": "A 3 anni il cuscinetto è almeno tre volte più largo",
              "linkedin": "Sui titoli a 3 anni il cuscinetto\nè almeno tre volte più largo"}[formato]
    sotto = {"articolo": f"Di quanto può aumentare il rendimento nei dodici mesi successivi prima che l'investimento\nchiuda in perdita, acquisto al {data_it(c['data'])}, in punti base (100 = 1 punto percentuale)",
             "social": f"Aumento del rendimento sopportabile in dodici mesi, in punti base, acquisto al {data_it(c['data'])}",
             "linkedin": f"Di quanto può aumentare il rendimento\nnei dodici mesi successivi prima della perdita,\nacquisto al {data_it(c['data'])}, in punti base"}[formato]
    g.intestazione(fig, titolo, sotto)
    fonte = {"articolo": f"Fonte: elaborazione Grinny Finanza su dati Banca d'Italia (BMK0200) e Bundesbank (BBSIS), estratti il {ESTRAZIONE}.",
             "social": f"Fonte: elab. Grinny Finanza su Banca d'Italia e Bundesbank, {ESTRAZIONE}.",
             "linkedin": f"Fonte: elaborazione Grinny Finanza su dati Banca\nd'Italia e Bundesbank, estratti il {ESTRAZIONE}."}[formato]
    nota_p = ("Titoli sintetici comprati alla pari. BTP: cedola semestrale; Bund: cedola annuale. Lordo d'imposta.") if formato == "articolo" else None
    g.piede(fig, fonte, nota_p)
    g.salva(fig, str(OUT / f"margini-3-10-anni_{formato}"))


# --------------------------------------------------------------------------------------
# 3. Come se la passa oggi chi ha comprato un decennale, per mese d'acquisto
# --------------------------------------------------------------------------------------
def grafico_esito(formato):
    eb = pd.read_csv(RIS / "esito_a_oggi_btp10.csv", parse_dates=["data_acquisto"]).set_index("data_acquisto")
    ed = pd.read_csv(RIS / "esito_a_oggi_bund10.csv", parse_dates=["data_acquisto"]).set_index("data_acquisto")
    assert (eb.loc["2021", "rend_cum"] < 0).all()  # il fatto del titolo
    fig, ax = g.figura(formato)
    x0, x1 = pd.Timestamp("2019-01-01"), pd.Timestamp("2025-10-01")
    lo, hi = -20, 25
    ax.set_xlim(x0, x1 + pd.Timedelta(days=10)); ax.set_ylim(lo, hi)
    ax.set_yticks(range(lo, hi + 1, 5 if formato != "social" else 10)); g.numeri_italiani(ax, x=False, pct=True, dec=0)
    ax.set_xticks([pd.Timestamp(f"{a}-01-01") for a in range(2019, 2026)])
    ax.set_xticklabels([str(a) for a in range(2019, 2026)])
    g.assi_stretti(ax, mdates.date2num(x0), mdates.date2num(x1), lo, hi)
    ax.axhline(0, color=g.ASSE, lw=0.7, zorder=2)
    ax.plot(ed.index, ed.rend_cum, color=g.PARAGONE, lw=g.LINEE["paragone"], zorder=3)
    ax.plot(eb.index, eb.rend_cum, color=g.PROTAGONISTA, lw=g.LINEE["protagonista"], zorder=4)
    a_capo = "\n"
    dx = pd.Timedelta(days=30)
    # nomi delle linee dove sono più lontane (inizio 2019): alla fine si incrociano e i nomi si confonderebbero
    stile = dict(fontsize=g.corpo(fig, "nota"), color=g.INCHIOSTRO, fontweight="semibold", ha="left", va="center")
    ax.text(pd.Timestamp("2019-02-01"), eb.loc["2019-03"].rend_cum.iloc[0] + 3.2, "BTP italiano", **stile)
    # il nome del Bund va sotto la sua linea nel 2023, dove c'è spazio fra la linea e la nota
    assert ed.loc["2023-01":"2023-12", "rend_cum"].min() > -4
    ax.text(pd.Timestamp("2023-02-01"), -7.0 if formato != "social" else -9.0, "Bund tedesco", **stile)
    pos0 = ax.get_position(); ax.set_position([pos0.x0, pos0.y0, pos0.width + 0.45 / fig.get_figwidth(), pos0.height])
    ax.set_xlabel("Mese in cui si è comprato il titolo" if formato != "social" else "Mese d'acquisto", labelpad=3)
    pos = ax.get_position(); alza = (0.18 if formato != "social" else 0.05) / fig.get_figheight()  # spazio per l'etichetta dell'asse sopra il piede
    ax.set_position([pos.x0, pos.y0 + alza, pos.width, pos.height - alza])

    # tre acquisti evidenziati, con il loro risultato (valori dal CSV)
    stretto = formato in ("linkedin", "social")
    mesi = {1: "gennaio", 5: "maggio", 8: "agosto"} if not stretto else {1: "gen", 5: "mag", 8: "ago"}
    def prep(v):  # "allo 0,65%", "all'8%", "al 2,75%"
        t = g.num(v, 2, True)
        return ("allo " if t.startswith("0") else "all'" if t.startswith(("8", "11")) else "al ") + t
    def punto(mese, testo_xy, ha):
        r = eb.loc[mese].iloc[0]
        ax.plot([r.name], [r.rend_cum], "o", color=g.PROTAGONISTA, ms=5, mec=g.SFONDO, mew=0.8, zorder=6)
        if stretto:
            etichetta = f"{mesi[r.name.month]} {r.name.year}\n{g.num(r.rend_cum, 1, True, segno=True)}"
        else:
            etichetta = f"{mesi[r.name.month]} {r.name.year}\n{prep(r.y_acquisto)}: {g.num(r.rend_cum, 1, True, segno=True)}"
        ax.annotate(etichetta, xy=(r.name, r.rend_cum), xytext=testo_xy, ha=ha, va="center",
                    fontsize=g.corpo(fig, "contesto"), color=g.INCHIOSTRO, fontweight="semibold", linespacing=1.2,
                    arrowprops=dict(arrowstyle="-", color=g.ASSE, lw=0.6, shrinkA=1, shrinkB=4))
    if formato != "social":
        punto("2021-08", (pd.Timestamp("2021-06-01") if not stretto else pd.Timestamp("2021-07-01"), -3.0 if not stretto else -4.0), "center")
    punto("2022-05", (pd.Timestamp("2021-12-01"), 10.5), "right")
    if formato != "social":
        punto("2023-01", (pd.Timestamp("2023-05-01") if not stretto else pd.Timestamp("2023-09-01"), 23.3 if formato != "social" else 21), "left")

    if formato != "social":
        g.nota(ax, pd.Timestamp("2022-11-01") if formato == "articolo" else pd.Timestamp("2022-06-01"), -14.5,
               "Ogni punto è un acquisto diverso,\nvalutato al 30 settembre 2026"
               if formato == "articolo" else "Ogni punto è un acquisto\ndiverso, valutato\nal 30/9/2026")

    titolo = {"articolo": "Chi ha comprato il BTP decennale nel 2021 è ancora in perdita",
              "social": "Chi ha comprato il BTP nel 2021 è ancora in perdita",
              "linkedin": "Chi ha comprato il BTP decennale\nnel 2021 è ancora in perdita"}[formato]
    sotto = {"articolo": "Rendimento cumulato, cedole comprese, di decennali sintetici acquistati alla pari in ciascun mese\ne valutati al 30 settembre 2026, in %",
             "social": "Rendimento cumulato al 30/9/2026, cedole comprese, per mese d'acquisto, in %",
             "linkedin": "Rendimento cumulato, cedole comprese,\ndi decennali acquistati alla pari in ciascun mese\ne valutati al 30 settembre 2026, in %"}[formato]
    g.intestazione(fig, titolo, sotto)
    fonte = {"articolo": f"Fonte: elaborazione Grinny Finanza su dati Banca d'Italia (BMK0200) e Deutsche Bundesbank (BBSIS), estratti il {ESTRAZIONE}.",
             "social": f"Fonte: elab. Grinny Finanza su Banca d'Italia e Bundesbank, {ESTRAZIONE}.",
             "linkedin": f"Fonte: elaborazione Grinny Finanza su dati Banca\nd'Italia e Bundesbank, estratti il {ESTRAZIONE}."}[formato]
    assert S['esito_a_oggi']['Bund 10 anni']['data_valutazione'] == S['esito_a_oggi']['BTP 10 anni']['data_valutazione'] == "2026-09-30"
    nota_p = ("Cedole più valore del titolo, lordo d'imposta; titoli valutati al rendimento della loro vita residua.") if formato == "articolo" else None
    g.piede(fig, fonte, nota_p)
    g.salva(fig, str(OUT / f"esito-per-mese-acquisto_{formato}"))


if __name__ == "__main__":
    for f in ("articolo", "social", "linkedin"):
        grafico_soglia(f)
        grafico_margini(f)
        grafico_esito(f)
    print("ok")
