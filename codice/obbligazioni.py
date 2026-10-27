"""Funzioni di prezzo per titoli a cedola fissa.

Convenzioni: rendimenti e cedole in percentuale annua (es. 4.5 = 4,5%),
prezzi per 100 di nominale, capitalizzazione alla stessa frequenza della cedola.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq


def prezzo(cedola: float, rendimento: float, anni: float, freq: int = 2) -> float:
    """Prezzo tel quel di un titolo a cedola fissa subito dopo il pagamento di una cedola.

    `anni` può non essere intero: in quel caso il primo flusso cade fra una frazione
    di periodo e si usa lo sconto composto anche sulla frazione (prezzo "sporco").
    """
    r = rendimento / 100 / freq
    c = cedola / freq
    n = anni * freq
    m = int(np.ceil(n - 1e-9))  # numero di flussi residui
    tempi = n - np.arange(m)  # in periodi: n, n-1, ..., tutti positivi; il rimborso cade a n
    flussi = np.full(m, c)
    flussi[0] += 100
    return float(np.sum(flussi / (1 + r) ** tempi))


def durata_modificata(cedola: float, rendimento: float, anni: float, freq: int = 2) -> float:
    """Durata finanziaria modificata, in anni, per differenza numerica."""
    h = 1e-4
    p0 = prezzo(cedola, rendimento, anni, freq)
    su = prezzo(cedola, rendimento + h, anni, freq)
    giu = prezzo(cedola, rendimento - h, anni, freq)
    return -(su - giu) / (2 * h / 100) / p0


def rendimento_un_anno(y0: float, y1: float, anni: float, freq: int, aliquota: float = 0.0) -> float:
    """Rendimento totale in % dopo un anno per chi compra alla pari al rendimento y0
    un titolo di `anni` anni e lo valuta dopo un anno al rendimento y1.
    Le cedole dell'anno sono sommate senza reinvestimento; `aliquota` le riduce."""
    cedole = y0 * (1 - aliquota)
    p1 = prezzo(y0, y1, anni - 1, freq)
    return cedole + p1 - 100


def soglia_pareggio(y0: float, anni: float, freq: int, aliquota: float = 0.0) -> float:
    """Rendimento fra un anno che rende nullo il rendimento totale (prezzo esatto)."""
    f = lambda y1: rendimento_un_anno(y0, y1, anni, freq, aliquota)
    return brentq(f, -5.0, 60.0)


def soglia_euristica(y0: float, anni: float, freq: int) -> float:
    """Approssimazione di Nangle: y0 + y0 / Dmod, con la Dmod che il titolo avrà fra un anno."""
    return y0 + y0 / durata_modificata(y0, y0, anni - 1, freq)
