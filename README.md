# Il cuscinetto di rendimento su BTP e Bund

Codice e dati per il pezzo di *La Finanza Secondo Grinny* sul "cuscinetto" dei titoli di Stato: di quanto deve salire il rendimento in un anno perché chi compra oggi un BTP (o un Bund) chiuda l'anno in perdita, e quanto spesso è successo dal 1999.

Spunto: Toby Nangle, "A bond is like a party balloon", FT Alphaville, ottobre 2026 (conto sui Treasury USA).

## Contenuto

| Cartella | Cosa c'è |
|---|---|
| `dati/` | I dati grezzi come scaricati dalle banche dati ufficiali (vedi sotto) |
| `codice/` | `obbligazioni.py` (prezzi e soglie), `analisi.py` (tutti i conti), `grafici.py` (grafici), `esempio_fuori_pari.py` (titoli comprati sopra o sotto 100), `grinny_style.py` (stile grafico) |
| `risultati/` | Le tabelle prodotte dal codice: soglie giornaliere, esiti per mese d'acquisto, `sintesi.json` con tutti i numeri citati |
| `grafici/` | I grafici in tre formati (articolo, social, LinkedIn), PNG e SVG, e i testi alternativi |
| `PIANO.md` | Il piano dell'analisi, scritto prima di guardare i risultati |

## Come rifare il conto

```bash
pip install -r requirements.txt
python codice/analisi.py                        # legge dati/, scrive risultati/
python codice/grafici.py                        # scrive grafici/ (tre formati per grafico)
python codice/esempio_fuori_pari.py             # esempio di titoli con cedole diverse
```

Per i grafici servono i font Inter e Lora; senza, il modulo di stile ripiega su font simili.

## Dati (in `dati/`, estratti il 25/10/2026)

| File | Fonte | Contenuto |
|---|---|---|
| `bdi_BMK0200_titoli_guida_giornalieri.csv` | Banca d'Italia, Base dati statistica, tavola BMK0200 | Rendimenti a scadenza lordi dei titoli di Stato guida (BTP 3, 5, 10, 30 anni, CCT, CTZ), giornalieri, 1988 – 30/9/2026 |
| `bbk_BBSIS_bund_rendimenti_par_giornalieri.csv` | Deutsche Bundesbank, BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R{02,03,05,10}XX.R.A.A._Z._Z.A | Rendimenti par a scadenza costante dei titoli federali, cedola annuale, giornalieri, 1997 – 23/10/2026 |
| `bce_IRS_decennali_IT_DE_mensili.csv` | BCE, IRS.M.{IT,DE}.L.L40.CI.0000.EUR.N.Z | Decennali di convergenza, medie mensili (controllo) |
| `eurostat_prc_hicp_minr_IT_DE.csv` | Eurostat, prc_hicp_minr (HICP, ECOICOP ver.2), totale | Indice HICP 2025=100 e variazione annua, Italia e Germania, 1996 – 9/2026 (estratto il 29/10/2026) |

Totali di controllo (somma della colonna del decennale): BdI 45.895,386; Bundesbank 19.249,52; BCE Italia 2.172,314.

## Metodo in breve

Il piano scritto prima dei risultati è in `PIANO.md`; il metodo completo è nel riquadro in fondo all'articolo su La Finanza Secondo Grinny. Ogni giorno si costruisce un titolo sintetico (non uno specifico ISIN): comprato alla pari, con cedola uguale al rendimento del giorno; un anno di detenzione; prezzo finale al rendimento della stessa scadenza osservato un anno dopo, come nel conto di Alphaville; soglia = rendimento che azzera cedole più variazione di prezzo, con il prezzo esatto. Nel metodo principale si ignorano rolldown, imposte sulle minusvalenze e costi. Le quote storiche si riferiscono a giornate d'acquisto, fortemente sovrapposte: non sono probabilità.

**Robustezza al rolldown** (`sintesi.json`, `robustezza_rolldown`): rivalutando il titolo dopo un anno al rendimento a 9 anni (interpolato fra 5 e 10), la quota di giornate d'acquisto in perdita dal 1999 scende dal 26,1% al 22,9% per il BTP decennale e dal 29,9% al 24,0% per il Bund.

## Risultati principali (`risultati/sintesi.json`)

- Al 30/9/2026: BTP 10 anni 4,59%, soglia 5,23% (+65 pb); BTP 3 anni 3,73%, soglia 5,73% (+200 pb); Bund 10 anni +49 pb; Bund 3 anni +177 pb.
- Giornate d'acquisto con perdita a un anno, 1999-2025: BTP 10 anni 26%, Bund 10 anni 30%, BTP 3 anni 20% (con rolldown: BTP 10 anni 23%, Bund 10 anni 24%).
- BTP decennale comprato il 2/5/2022 al 2,75%: +5,7% al 30/9/2026; −8,6% reale (HICP Italia +15,7% fra maggio 2022 e settembre 2026).
- BTP decennale comprato il 12/2/2021 allo 0,44%: −11,3% al 30/9/2026; −30,4% reale.

## Come si sono ottenuti i dati

Tutte le serie vengono da banche dati statistiche ufficiali, non da PDF. Bundesbank, BCE ed Eurostat sono state interrogate con le loro interfacce pubbliche; la serie Banca d'Italia è la tavola BMK0200 della Base dati statistica, consultabile senza registrazione su infostat.bancaditalia.it. Il decennale italiano mensile della BCE (IRS.M.IT.L.L40.CI.0000.EUR.N.Z) coincide con le medie mensili Banca d'Italia ed è scaricabile senza alcun accesso.
