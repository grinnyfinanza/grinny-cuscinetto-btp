"""Esempio per il testo: 10.000 euro in un BTP nuovo comprato a 100 il 30/9/2026, con cedola uguale
al rendimento del giorno, e quanto vale dopo un anno a seconda di dove sono i rendimenti.

Come nel metodo principale, dopo un anno il titolo si valuta al rendimento della stessa scadenza
(decennale o triennale) osservato in quel momento, senza roll-down. Cedole lorde, senza reinvestimento.

Uso:  python codice/esempio_10000_euro.py   (scrive risultati/esempio_10000_euro.csv)
"""
from pathlib import Path

import pandas as pd

from obbligazioni import prezzo, rendimento_un_anno, soglia_pareggio

QUI = Path(__file__).resolve().parent
DATI, OUT = QUI.parent / "dati", QUI.parent / "risultati"
CAPITALE = 10_000
DATA = "2026-09-30"

btp = pd.read_csv(DATI / "bdi_BMK0200_titoli_guida_giornalieri.csv", parse_dates=["data"]).set_index("data")
righe = []
for nome, col, anni in (("BTP 10 anni", "btp_10a", 10), ("BTP 3 anni", "btp_3a", 3)):
    y0 = float(btp.loc[DATA, col])
    s = soglia_pareggio(y0, anni, 2)
    scenari = {"invariato": y0, "soglia di pareggio": s, "+1 punto": y0 + 1, "6%": 6.0}
    for scenario, y1 in scenari.items():
        valore = prezzo(y0, y1, anni - 1, 2) / 100 * CAPITALE
        cedole = y0 / 100 * CAPITALE
        righe.append(dict(titolo=nome, scenario=scenario, rendimento_acquisto=round(y0, 4),
                          rendimento_dopo_un_anno=round(y1, 4), valore_titolo_euro=round(valore),
                          cedole_euro=round(cedole), saldo_euro=round(valore + cedole - CAPITALE),
                          rendimento_anno_pct=round(rendimento_un_anno(y0, y1, anni, 2), 2)))

tab = pd.DataFrame(righe)
tab.to_csv(OUT / "esempio_10000_euro.csv", index=False)
print(tab.to_string(index=False))
