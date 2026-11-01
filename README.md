# Il cuscinetto di rendimento su BTP e Bund

Codice e dati per il pezzo di *La Finanza Secondo Grinny* sul "cuscinetto" dei titoli di Stato: di quanto deve salire il rendimento in un anno perché chi compra oggi un BTP (o un Bund) chiuda l'anno in perdita, e quanto spesso è successo dal 1999.

Spunto: Toby Nangle, "A bond is like a party balloon", FT Alphaville, ottobre 2026 (conto sui Treasury USA).

## Contenuto

| Cartella | Cosa c'è |
|---|---|
| `dati/` | I dati grezzi come scaricati dalle banche dati ufficiali (vedi sotto) |
| `codice/` | `obbligazioni.py` (prezzi e soglie), `analisi.py` (tutti i conti), `grafici.py` (grafici), `esempio_fuori_pari.py` (titoli comprati sopra o sotto 100), `esempio_10000_euro.py` (l'esempio in euro dell'articolo), `grinny_style.py` (stile grafico, con il logo `grinny-logo-originale.jpg`) |
| `risultati/` | Le tabelle prodotte dal codice: soglie giornaliere, esiti per mese d'acquisto, `sintesi.json` con tutti i numeri citati |
| `grafici/` | I grafici in tre formati (articolo, social, LinkedIn), PNG e SVG, e i testi alternativi |
| `PIANO.md` | Il piano dell'analisi, scritto prima di guardare i risultati |

## Come rifare il conto

```bash
pip install -r requirements.txt
python codice/analisi.py                        # legge dati/, scrive risultati/
python codice/grafici.py                        # scrive grafici/ (tre formati per grafico)
python codice/esempio_fuori_pari.py             # esempio di titoli con cedole diverse
python codice/esempio_10000_euro.py             # 10.000 euro nel BTP del 30/9/2026, tre scenari a un anno
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

Il piano scritto prima dei risultati è in `PIANO.md`; il metodo completo è nella sezione qui sotto, l'articolo su La Finanza Secondo Grinny ne riporta una sintesi. Ogni giorno si costruisce un titolo sintetico (non uno specifico ISIN): comprato alla pari, con cedola uguale al rendimento del giorno; un anno di detenzione; prezzo finale al rendimento della stessa scadenza osservato un anno dopo, come nel conto di Alphaville; soglia = rendimento che azzera cedole più variazione di prezzo, con il prezzo esatto. Nel metodo principale si ignorano rolldown, imposte sulle minusvalenze e costi. Le quote storiche si riferiscono a giornate d'acquisto, fortemente sovrapposte: non sono probabilità.

**Robustezza al rolldown** (`sintesi.json`, `robustezza_rolldown`): rivalutando il titolo dopo un anno al rendimento a 9 anni (interpolato fra 5 e 10), la quota di giornate d'acquisto in perdita dal 1999 scende dal 26,1% al 22,9% per il BTP decennale e dal 29,9% al 24,0% per il Bund.

## Metodo completo

È il riquadro sul metodo nella versione lunga: nell'articolo ne resta una sintesi, qui ci sono tutti i passaggi e i numeri citati nel testo.

**Dati.** BTP: Banca d'Italia, [Base dati statistica](https://infostat.bancaditalia.it/), tavola BMK0200, rendimenti a scadenza lordi dei titoli guida, giornalieri, estratti il 25/10/2026, ultimo dato 30/9/2026. Le medie di settembre ricalcolate dai dati giornalieri (3,56%, 4,36% e 5,01% su 3, 10 e 30 anni) coincidono con [Mercato finanziario del 15 ottobre 2026](https://www.bancaditalia.it/pubblicazioni/mercato-finanziario/2026-mercato-finanziario/statistiche_MFN_20261015.pdf). Bund: Deutsche Bundesbank, [banca dati statistica](https://api.statistiken.bundesbank.de/doc/index.html), serie BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R{02,03,05,10}XX, rendimenti par a scadenza costante derivati dalla curva, cedola annuale; per i confronti si usa il 30/9/2026. Inflazione: Eurostat, prc_hicp_minr, indice HICP Italia 2025=100, estratto il 29/10/2026, ultimo dato settembre 2026 (+4,2% su base annua): 82,4 a febbraio 2021, 90,7 a maggio 2022, 104,9 a settembre 2026. Controllo: decennali mensili BCE (IRS), identici alla serie Banca d'Italia per l'Italia; per la Germania lo scarto medio è di 7,7 punti base, per la diversa costruzione delle serie.

**Verifica sul conto di Nangle.** Sul decennale americano al 5,1% la nostra soglia esce al 5,84%, l'articolo di Alphaville riporta 5,83%.

**Titolo sintetico.** Ogni giorno: acquisto alla pari, cedola uguale al rendimento del giorno, scadenza intera di 3 o 10 anni; cedole semestrali per il BTP, annuali per il Bund. Il modello astrae dal calendario effettivo delle cedole e dal rateo di uno specifico ISIN.

**Rendimento a dodici mesi.** Cedole dell'anno, senza reinvestimento, più il prezzo esatto a t + 365 giorni (ultimo giorno di mercato precedente), ottenuto scontando ogni flusso futuro. La soglia è il rendimento che azzera questa somma. I tre decennali con cedole dell'1%, del 4,59% e del 7% hanno tutti rendimento a scadenza del 4,59% e sono valutati allo stesso modo (`risultati/esempio_fuori_pari.csv`). La scorciatoia di Nangle (rendimento diviso duration modificata a un anno dall'acquisto) dà soglie inferiori in media fra 1 e 3 punti base; sul triennale del 30/9/2026, 195 punti base contro 200.

**Roll-down.** Nel metodo principale il titolo dopo un anno si valuta al rendimento della scadenza originaria, come fa Alphaville. Robustezza: con il rendimento a 9 anni interpolato fra 5 e 10 anni, le giornate d'acquisto in perdita dal 1999 scendono dal 26,1% al 22,9% per il BTP decennale e dal 29,9% al 24,0% per il Bund. Al 30/9/2026 il rendimento BTP a 9 anni interpolato è il 4,47%: con curva invariata e uno spostamento parallelo, il margine sarebbe di circa 77 punti base invece di 65.

**Giornate d'acquisto.** Dal 4/1/1999 al 30/9/2025: 6.800 giornate per il BTP decennale, 1.778 con perdita a un anno; il periodo continuo più lungo va dall'8/10/2020 al 9/6/2022 (426 giornate). Sull'intera serie disponibile, dal 1991, la quota del BTP decennale è il 24%. Perdita a un anno peggiore: BTP decennale comprato il 12/10/2021 (−27,1%; la peggiore prima del 2021 è del 9/11/2010, −17,9%); Bund decennale comprato il 2/3/2022 (−22,5%; prima del 2021, −9,3% nel gennaio 1999). Confronto fra le due crisi: rialzo a un anno di 3,39 punti per il BTP comprato il 9/11/2010 al 4,03% e di 3,88 punti per quello comprato il 12/10/2021 allo 0,95%; applicando a quest'ultimo il rialzo del 2010, la perdita sarebbe stata del 24,1% (`sintesi.json`, `confronto_2010_2021`).

**Spread.** Differenza fra il decennale Banca d'Italia e il decennale Bundesbank; medie annue di 200 punti base nel 2022 e di 93 nel 2025. I 14 punti base di allargamento di pareggio valgono con il Bund invariato; con una variazione del Bund di −100, +100 e +200 punti base diventano circa 9, 18 e 23. Dal 1999 il BTP decennale ha reso meno del Bund, su un anno, nel 44% delle giornate d'acquisto; dal 2022 nel 3%.

**Esito per mese d'acquisto.** Titolo comprato il primo giorno di mercato di ogni mese dal 2019, valutato al 30/9/2026 al rendimento interpolato sulla sua vita residua (BTP: nodi a 3, 5, 10, 30 anni; Bund: 2, 3, 5, 10), con cedole incassate e rateo. Il reale è deflazionato con l'indice HICP Italia.

**Altre avvertenze.** Risultati al lordo d'imposta, salvo la sensibilità semplificata al 12,5% sulle cedole; nessun costo di negoziazione. La serie italiana segue i titoli guida, quella tedesca una curva a scadenza costante: differenze di pochi punti base fra i due paesi non vanno sovrainterpretate. Il dato di fine ottobre (rendimento intorno al 4,5%, spread di circa 117 punti) viene dalle quotazioni riportate dalla stampa e non dalla serie Banca d'Italia, che quando abbiamo fatto il conto arrivava al 30 settembre; il margine di circa 63 punti base è calcolato con lo stesso metodo su un rendimento del 4,52%.

**Scelte e varianti.** Il piano dell'analisi è stato scritto prima di guardare i risultati. Aggiunte successive, dichiarate: l'esito per mese d'acquisto, il confronto con lo spread, la robustezza al roll-down e il confronto fra il 2010 e il 2021.

## Risultati principali (`risultati/sintesi.json`)

- Al 30/9/2026: BTP 10 anni 4,59%, soglia 5,23% (+65 pb); BTP 3 anni 3,73%, soglia 5,73% (+200 pb); Bund 10 anni +49 pb; Bund 3 anni +177 pb.
- Giornate d'acquisto con perdita a un anno, 1999-2025: BTP 10 anni 26%, Bund 10 anni 30%, BTP 3 anni 20% (con rolldown: BTP 10 anni 23%, Bund 10 anni 24%).
- BTP decennale comprato il 2/5/2022 al 2,75%: +5,7% al 30/9/2026; −8,6% reale (HICP Italia +15,7% fra maggio 2022 e settembre 2026).
- BTP decennale comprato il 12/2/2021 allo 0,44%: −11,3% al 30/9/2026; −30,4% reale.

## Come si sono ottenuti i dati

Tutte le serie vengono da banche dati statistiche ufficiali, non da PDF. Bundesbank, BCE ed Eurostat sono state interrogate con le loro interfacce pubbliche; la serie Banca d'Italia è la tavola BMK0200 della Base dati statistica, consultabile senza registrazione su infostat.bancaditalia.it. Il decennale italiano mensile della BCE (IRS.M.IT.L.L40.CI.0000.EUR.N.Z) coincide con le medie mensili Banca d'Italia ed è scaricabile senza alcun accesso.
