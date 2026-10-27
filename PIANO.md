# Piano dell'analisi (scritto prima di guardare i risultati)

Data: 25 ottobre 2026. Spunto: T. Nangle, FT Alphaville, "A bond is like a party balloon" (ottobre 2026), che fa il conto sui Treasury USA.

## Domanda

Per ogni giorno di mercato: a quale livello dovrebbe salire il rendimento fra un anno perché chi compra oggi un BTP (o un Bund) chiuda l'anno con un rendimento totale negativo? E com'è andata davvero: quanto spesso, e quando, chi comprava ha perso su un orizzonte di un anno?

## Dati

- BTP: Banca d'Italia, Base dati statistica, tavola BMK0200 "Titoli di Stato guida: rendimenti a scadenza lordi (dati giornalieri)". Serie BTP 3 e 10 anni (anche 5 e 30 per interpolare). Fino al 30/9/2026.
- Bund: Deutsche Bundesbank, serie BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R{02,03,05,10}XX.R.A.A._Z._Z.A, rendimenti par a scadenza costante derivati dalla curva, cedola annuale. Fino al 23/10/2026.
- Controllo: BCE, IRS.M.{IT,DE}.L.L40.CI.0000.EUR.N.Z (decennale di convergenza, medie mensili); Banca d'Italia, "Mercato finanziario" del 15/10/2026 (medie di settembre 2026).
- Inflazione: BCE, ICP.M.{IT,DE}.N.000000.4.INX (indice HICP), disponibile fino a dicembre 2025.

## Metodo principale (deciso ora)

1. Il giorno t si compra alla pari un titolo con scadenza N anni (N = 10 e 3) e cedola pari al rendimento del giorno, y_t. Cedola semestrale per il BTP, annuale per il Bund.
2. Lo si tiene un anno (t + 365 giorni; se è festivo, l'ultimo giorno di mercato precedente).
3. Rendimento totale = cedole incassate nell'anno + variazione di prezzo. Il prezzo a fine anno è quello di un titolo con N − 1 anni residui, valutato al rendimento della stessa scadenza N osservato quel giorno (y_{t+1}). Come Nangle, si ignora il rolldown (l'effetto della pendenza della curva).
4. Soglia di pareggio y*: il rendimento fra un anno che azzera il rendimento totale, trovato con il prezzo esatto (non con l'approssimazione della duration).
5. Esito realizzato: perdita se y_{t+1} > y*.
6. Finestra principale: dal 1° gennaio 1999 (nascita dell'euro) all'ultima data con esito noto. Il BTP a 3 anni ha un buco nel 1992-1995, che resta fuori dalla finestra principale.

## Cosa sarebbe banale e cosa no

- Banale: "più alto il rendimento, più spesso il cuscinetto". È aritmetica, il pezzo lo spiega ma non lo presenta come scoperta.
- Interessante: quanto spesso il cuscinetto è stato bucato in Italia e in Germania; in quali episodi (2011 e 2022 hanno cause diverse: credito contro tassi); quanto del cuscinetto in più del BTP è semplicemente lo spread, cioè il prezzo del rischio di credito; come se la passa chi ha comprato al minimo dei rendimenti (l'equivalente del "maggio 2022" di Nangle), in termini nominali e reali.

## Robustezza (decisa ora)

- Soglia con l'approssimazione di Nangle (y + y/Dmod) contro prezzo esatto.
- Decennale giornaliero Banca d'Italia contro medie mensili BCE.
- Finestra intera disponibile contro finestra dal 1999.
- Cedole al netto dell'imposta del 12,5% (sensibilità; le minusvalenze non sono trattate).

## Per il conto "chi ha comprato al minimo"

Il titolo comprato invecchia: dopo k anni la vita residua è N − k. Per valutarlo si usa il rendimento interpolato linearmente fra le scadenze guida disponibili (3, 5, 10, 30 anni; sotto i 3 anni si tiene il 3 anni). Approssimazione da dichiarare.
