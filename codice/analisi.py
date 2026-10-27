"""Cuscinetto di rendimento su BTP e Bund: soglie di pareggio a un anno ed esiti realizzati.

Uso:  python codice/analisi.py      (dalla cartella principale del progetto)
Legge i CSV in dati/, scrive i risultati in risultati/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from obbligazioni import (durata_modificata, prezzo, rendimento_un_anno,
                          soglia_euristica, soglia_pareggio)

BASE = Path(__file__).resolve().parents[1]
DATI = BASE / "dati"
RIS = BASE / "risultati"
RIS.mkdir(exist_ok=True)

INIZIO = "1999-01-01"  # finestra principale, decisa nel PIANO.md


def carica():
    btp = pd.read_csv(DATI / "bdi_BMK0200_titoli_guida_giornalieri.csv", parse_dates=["data"]).set_index("data")
    bund = pd.read_csv(DATI / "bbk_BBSIS_bund_rendimenti_par_giornalieri.csv", parse_dates=["data"]).set_index("data")
    bce = pd.read_csv(DATI / "bce_IRS_decennali_IT_DE_mensili.csv")
    bce["mese"] = pd.PeriodIndex(bce["mese"], freq="M")
    hicp = pd.read_csv(DATI / "bce_ICP_hicp_IT_DE_mensili.csv")
    hicp["mese"] = pd.PeriodIndex(hicp["mese"], freq="M")
    return btp, bund, bce.set_index("mese"), hicp.set_index("mese")


def valore_a_un_anno(s: pd.Series) -> pd.Series:
    """Per ogni data t, il valore della serie all'ultima data disponibile <= t + 365 giorni.
    NaN se quella data è oltre la fine dei dati o se dista più di 7 giorni da t + 365."""
    s = s.dropna()
    target = s.index + pd.Timedelta(days=365)
    pos = s.index.searchsorted(target, side="right") - 1
    pos = np.clip(pos, 0, len(s) - 1)
    trovate = s.index[pos]
    ok = (target <= s.index[-1]) & ((target - trovate) <= pd.Timedelta(days=7))
    out = pd.Series(np.where(ok, s.values[pos], np.nan), index=s.index)
    return out


def tabella_soglie(y: pd.Series, anni: int, freq: int, nome: str) -> pd.DataFrame:
    y = y.dropna()
    y1 = valore_a_un_anno(y)
    df = pd.DataFrame({"y0": y, "y1": y1})
    df["soglia"] = [soglia_pareggio(v, anni, freq) for v in df["y0"]]
    df["soglia_euristica"] = [soglia_euristica(v, anni, freq) for v in df["y0"]]
    df["soglia_netta"] = [soglia_pareggio(v, anni, freq, aliquota=0.125) for v in df["y0"]]
    df["margine_pb"] = (df["soglia"] - df["y0"]) * 100
    df["rend_1a"] = [rendimento_un_anno(a, b, anni, freq) if pd.notna(b) else np.nan
                     for a, b in zip(df["y0"], df["y1"])]
    df["perdita"] = np.where(df["y1"].notna(), df["y1"] > df["soglia"], np.nan)
    df["serie"] = nome
    return df


def quote_perdita(df: pd.DataFrame, inizio=INIZIO, fine=None) -> dict:
    d = df.loc[inizio:fine].dropna(subset=["y1"])
    return {"giorni": int(len(d)), "quota_perdita": float(d["perdita"].mean()),
            "dal": str(d.index.min().date()), "al": str(d.index.max().date())}


def episodi_perdita(df: pd.DataFrame, inizio=INIZIO, minimo_giorni=5) -> list:
    """Intervalli di date d'acquisto consecutive con perdita a un anno."""
    d = df.loc[inizio:].dropna(subset=["y1"])
    p = d["perdita"].astype(bool)
    gruppi = (p != p.shift()).cumsum()
    out = []
    for _, g in d[p].groupby(gruppi[p]):
        if len(g) >= minimo_giorni:
            out.append({"da": str(g.index.min().date()), "a": str(g.index.max().date()),
                        "giorni": int(len(g)), "rend_1a_peggiore": round(float(g["rend_1a"].min()), 2),
                        "y0_min": round(float(g["y0"].min()), 2), "y0_max": round(float(g["y0"].max()), 2)})
    return out


def curva_interpolata(btp: pd.DataFrame) -> pd.DataFrame:
    """Rendimenti BTP per scadenza residua qualsiasi, interpolando fra 3, 5, 10 e 30 anni."""
    nodi = {3: "btp_3a", 5: "btp_5a", 10: "btp_10a", 30: "btp_30a"}
    return btp[list(nodi.values())].rename(columns={v: k for k, v in nodi.items()})


def rendimento_interp(riga: pd.Series, residua: float) -> float:
    r = riga.dropna()
    if r.empty:
        return np.nan
    x = np.array(r.index, dtype=float)
    return float(np.interp(residua, x, r.values))  # sotto i 3 anni resta il 3 anni


def compra_e_tieni(btp: pd.DataFrame, data_acquisto: str, anni: int = 10, freq: int = 2) -> pd.DataFrame:
    """Valore nel tempo (cedole incassate cumulate + prezzo) di un BTP decennale comprato alla pari."""
    curva = curva_interpolata(btp).dropna(how="all")
    t0 = curva.index[curva.index.searchsorted(pd.Timestamp(data_acquisto))]
    y0 = btp.loc[t0, "btp_10a"] if anni == 10 else btp.loc[t0, f"btp_{anni}a"]
    righe = []
    for t, riga in curva.loc[t0:].iterrows():
        trascorsi = (t - t0).days / 365.25
        residua = anni - trascorsi
        if residua <= 0.05:
            break
        y = rendimento_interp(riga, residua)
        cedole = y0 / freq * np.floor(trascorsi * freq + 1e-9)
        # prezzo tel quel: include il rateo maturato dall'ultima cedola
        p = prezzo(y0, y, residua, freq)
        righe.append((t, y, cedole, p, cedole + p - 100))
    out = pd.DataFrame(righe, columns=["data", "y_residua", "cedole_cum", "prezzo_tq", "rend_cum"]).set_index("data")
    out.attrs["y0"] = float(y0)
    out.attrs["data_acquisto"] = str(t0.date())
    return out


def esito_a_oggi(curva: pd.DataFrame, y_acq: pd.Series, anni: int, freq: int, dal: str) -> pd.DataFrame:
    """Per ogni data d'acquisto (primo giorno di mercato di ogni mese dal `dal`), rendimento
    totale cumulato all'ultima data disponibile di un titolo di `anni` anni comprato alla pari.
    Il titolo invecchiato si valuta al rendimento interpolato sulla curva dell'ultima data."""
    curva = curva.dropna(how="all")
    t_fine = curva.index.max()
    riga_fine = curva.loc[t_fine]
    y = y_acq.dropna().loc[dal:]
    date = y.groupby(y.index.to_period("M")).head(1).index
    out = []
    for t0 in date:
        trascorsi = (t_fine - t0).days / 365.25
        residua = anni - trascorsi
        if trascorsi < 1 or residua <= 0.05:
            continue
        y0 = float(y.loc[t0])
        yr = rendimento_interp(riga_fine, residua)
        cedole = y0 / freq * np.floor(trascorsi * freq + 1e-9)
        out.append((t0, y0, residua, yr, cedole + prezzo(y0, yr, residua, freq) - 100, trascorsi))
    df = pd.DataFrame(out, columns=["data_acquisto", "y_acquisto", "residua", "y_oggi", "rend_cum", "anni_trascorsi"])
    df["rend_annuo"] = ((1 + df.rend_cum / 100) ** (1 / df.anni_trascorsi) - 1) * 100
    df.attrs["data_valutazione"] = str(t_fine.date())
    return df.set_index("data_acquisto")


def verifiche(btp, bund, bce) -> dict:
    v = {}
    # 1) Media di settembre 2026 dei BTP guida contro "Mercato finanziario" del 15/10/2026: 3,56 / 4,36 / 5,01
    sett = btp.loc["2026-09"].mean()
    v["bdi_media_set_2026"] = {k: round(float(sett[k]), 2) for k in ["btp_3a", "btp_10a", "btp_30a"]}
    v["bdi_pubblicato_set_2026"] = {"btp_3a": 3.56, "btp_10a": 4.36, "btp_30a": 5.01}
    # 2) Decennale BdI giornaliero (media mensile) contro BCE IRS mensile
    m = btp["btp_10a"].resample("ME").mean().to_period("M")
    k = bund["bund_10a"].resample("ME").mean().to_period("M")
    j = pd.concat([m.rename("bdi"), bce["it_10a"].rename("bce_it"), k.rename("bbk"), bce["de_10a"].rename("bce_de")], axis=1).loc["1999-01":]
    j = j.dropna()
    v["it_diff_bdi_bce_pb"] = {"media": round(float((j.bdi - j.bce_it).mean() * 100), 1),
                               "media_abs": round(float((j.bdi - j.bce_it).abs().mean() * 100), 1),
                               "max_abs": round(float((j.bdi - j.bce_it).abs().max() * 100), 1), "mesi": int(len(j))}
    v["de_diff_bbk_bce_pb"] = {"media": round(float((j.bbk - j.bce_de).mean() * 100), 1),
                               "media_abs": round(float((j.bbk - j.bce_de).abs().mean() * 100), 1),
                               "max_abs": round(float((j.bbk - j.bce_de).abs().max() * 100), 1)}
    # 3) Esempio Nangle: decennale USA al 5,1% -> soglia 5,83% (articolo)
    v["nangle_usa"] = {"soglia_esatta": round(soglia_pareggio(5.1, 10, 2), 2),
                       "soglia_euristica": round(soglia_euristica(5.1, 10, 2), 2), "articolo": 5.83}
    return v


def main():
    btp, bund, bce, hicp = carica()
    tab = {
        "BTP 10 anni": tabella_soglie(btp["btp_10a"], 10, 2, "BTP 10 anni"),
        "BTP 3 anni": tabella_soglie(btp["btp_3a"], 3, 2, "BTP 3 anni"),
        "Bund 10 anni": tabella_soglie(bund["bund_10a"], 10, 1, "Bund 10 anni"),
        "Bund 3 anni": tabella_soglie(bund["bund_3a"], 3, 1, "Bund 3 anni"),
    }
    pd.concat(tab.values()).to_csv(RIS / "soglie_giornaliere.csv", float_format="%.4f")

    sintesi = {"verifiche": verifiche(btp, bund, bce), "serie": {}}
    for nome, df in tab.items():
        ultimo = df.dropna(subset=["y0"]).iloc[-1]
        ultimo_noto = df.dropna(subset=["y1"]).index.max()
        sintesi["serie"][nome] = {
            "ultima_data": str(df.index.max().date()),
            "ultimo_rendimento": round(float(ultimo.y0), 2),
            "soglia_esatta": round(float(ultimo.soglia), 2),
            "soglia_euristica": round(float(ultimo.soglia_euristica), 2),
            "soglia_netta_12_5": round(float(ultimo.soglia_netta), 2),
            "margine_pb": round(float(ultimo.margine_pb)),
            "ultima_data_esito_noto": str(ultimo_noto.date()),
            "dal_1999": quote_perdita(df),
            "intera_serie": quote_perdita(df, inizio=None),
            "2009_2021": quote_perdita(df, "2009-01-01", "2021-12-31"),
            "dal_2022": quote_perdita(df, "2022-01-01"),
            "episodi": episodi_perdita(df),
            "diff_soglia_esatta_euristica_pb_media": round(float((df.soglia - df.soglia_euristica).loc[INIZIO:].mean() * 100), 1),
        }
    # Cuscinetto del BTP in più rispetto al Bund = differenza di margini; spread = differenza di rendimenti
    m = pd.concat([tab["BTP 10 anni"]["margine_pb"].rename("btp"), tab["Bund 10 anni"]["margine_pb"].rename("bund"),
                   btp["btp_10a"].rename("y_btp"), bund["bund_10a"].rename("y_bund")], axis=1, sort=True).dropna()
    sintesi["confronto_ultimo_giorno_comune"] = {
        "data": str(m.index.max().date()),
        "margine_btp_pb": round(float(m.btp.iloc[-1])), "margine_bund_pb": round(float(m.bund.iloc[-1])),
        "spread_pb": round(float((m.y_btp - m.y_bund).iloc[-1] * 100)),
    }

    # Chi ha comprato al minimo: decennale BTP al rendimento più basso dal 2019
    y10 = btp["btp_10a"].dropna()
    data_min = y10.loc["2019-01-01":].idxmin()
    cet = compra_e_tieni(btp, str(data_min.date()))
    cet.to_csv(RIS / "compra_e_tieni_btp10_minimo.csv", float_format="%.4f")
    peggiore = cet["rend_cum"].idxmin()
    torna_pos = cet.loc[peggiore:][cet.loc[peggiore:, "rend_cum"] >= 0]
    # reale: deflazione con HICP Italia, fino all'ultimo mese disponibile
    h = hicp["hicp_it"].dropna()
    ultimo_mese = h.index.max()
    fine_reale = cet.loc[:ultimo_mese.end_time].index.max()
    inf_cum = h.loc[ultimo_mese] / h.loc[pd.Period(data_min, "M")] - 1
    nom_fine = cet.loc[fine_reale, "rend_cum"] / 100
    sintesi["compra_al_minimo"] = {
        "data_acquisto": cet.attrs["data_acquisto"], "rendimento_acquisto": round(cet.attrs["y0"], 2),
        "rend_cum_peggiore": round(float(cet.rend_cum.min()), 1), "data_peggiore": str(peggiore.date()),
        "torna_positivo_dal": str(torna_pos.index.min().date()) if len(torna_pos) else None,
        "rend_cum_ultimo": round(float(cet.rend_cum.iloc[-1]), 1), "ultima_data": str(cet.index.max().date()),
        "reale_fino_a": str(ultimo_mese), "nominale_a_quella_data": round(float(nom_fine * 100), 1),
        "inflazione_cumulata": round(float(inf_cum * 100), 1),
        "reale_a_quella_data": round(float(((1 + nom_fine) / (1 + inf_cum) - 1) * 100), 1),
    }
    # Esteso dopo il piano (dichiarato): esito a oggi per ogni mese d'acquisto dal 2019, BTP e Bund,
    # per non dipendere dalla sola data del minimo.
    curva_bund = bund[["bund_2a", "bund_3a", "bund_5a", "bund_10a"]].rename(
        columns={"bund_2a": 2, "bund_3a": 3, "bund_5a": 5, "bund_10a": 10})
    e_btp = esito_a_oggi(curva_interpolata(btp), btp["btp_10a"], 10, 2, "2019-01-01")
    e_bund = esito_a_oggi(curva_bund, bund["bund_10a"], 10, 1, "2019-01-01")
    e_btp.to_csv(RIS / "esito_a_oggi_btp10.csv", float_format="%.4f")
    e_bund.to_csv(RIS / "esito_a_oggi_bund10.csv", float_format="%.4f")

    def riassumi(e):
        neg = e[e.rend_cum < 0]
        return {"data_valutazione": e.attrs["data_valutazione"], "mesi": int(len(e)),
                "mesi_in_perdita": int(len(neg)),
                "ultimo_mese_acquisto_in_perdita": str(neg.index.max().date()) if len(neg) else None,
                "primo_mese_acquisto_in_perdita": str(neg.index.min().date()) if len(neg) else None,
                "peggiore": [str(e.rend_cum.idxmin().date()), round(float(e.rend_cum.min()), 1)],
                "mag_2022": {k: round(float(v), 2) for k, v in e.loc["2022-05"].iloc[0].items()}}
    sintesi["esito_a_oggi"] = {"BTP 10 anni": riassumi(e_btp), "Bund 10 anni": riassumi(e_bund)}

    # Stessa data per tutti (30/9/2026, ultima data Banca d'Italia)
    data_comune = min(tab["BTP 10 anni"].index.max(), tab["Bund 10 anni"].index.max())
    sintesi["alla_data_comune"] = {"data": str(data_comune.date())}
    for nome, df in tab.items():
        r = df.loc[:data_comune].iloc[-1]
        sintesi["alla_data_comune"][nome] = {"rendimento": round(float(r.y0), 2), "soglia": round(float(r.soglia), 2),
                                             "margine_pb": round(float(r.margine_pb))}

    # Il lato credito (pannello destro di Nangle): di quanto deve allargarsi lo spread BTP-Bund in un anno
    # perché il BTP renda meno del Bund, a parità di rendimento del Bund? E com'è andata davvero?
    from scipy.optimize import brentq
    yb, yd = float(btp.loc[data_comune, "btp_10a"]), float(bund.loc[:data_comune, "bund_10a"].iloc[-1])
    rd = rendimento_un_anno(yd, yd, 10, 1)
    dy = brentq(lambda d: rendimento_un_anno(yb, yb + d, 10, 2) - rd, -5, 10)
    rel = pd.concat([tab["BTP 10 anni"]["rend_1a"].rename("btp"), tab["Bund 10 anni"]["rend_1a"].rename("bund")],
                    axis=1, sort=True).dropna().loc[INIZIO:]
    sintesi["spread"] = {
        "data": str(data_comune.date()), "spread_pb": round((yb - yd) * 100),
        "allargamento_pareggio_pb": round(dy * 100),
        "quota_giorni_btp_sotto_bund_1a_dal_1999": round(float((rel.btp < rel.bund).mean()), 3),
        "quota_giorni_btp_sotto_bund_1a_dal_2022": round(float((rel.loc["2022":].btp < rel.loc["2022":].bund).mean()), 3),
        "giorni": int(len(rel)),
    }

    # Il "maggio 2022" di Nangle, in termini nominali e reali (reale fino all'ultimo mese HICP)
    cet22 = compra_e_tieni(btp, "2022-05-02")
    cet22.to_csv(RIS / "compra_e_tieni_btp10_mag2022.csv", float_format="%.4f")
    fine_r = cet22.loc[:ultimo_mese.end_time].index.max()
    nom22 = cet22.loc[fine_r, "rend_cum"] / 100
    inf22 = h.loc[ultimo_mese] / h.loc[pd.Period("2022-05", "M")] - 1
    sintesi["maggio_2022"] = {"data_acquisto": cet22.attrs["data_acquisto"], "rendimento_acquisto": round(cet22.attrs["y0"], 2),
                              "rend_cum_peggiore": round(float(cet22.rend_cum.min()), 1),
                              "data_peggiore": str(cet22.rend_cum.idxmin().date()),
                              "rend_cum_ultimo": round(float(cet22.rend_cum.iloc[-1]), 1),
                              "nominale_dic_2025": round(float(nom22 * 100), 1),
                              "inflazione_mag22_dic25": round(float(inf22 * 100), 1),
                              "reale_dic_2025": round(float(((1 + nom22) / (1 + inf22) - 1) * 100), 1)}

    (RIS / "sintesi.json").write_text(json.dumps(sintesi, indent=2, ensure_ascii=False))
    print(json.dumps(sintesi, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
