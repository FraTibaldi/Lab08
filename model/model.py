from database.distributore_DAO import DistributoreDAO
from model.distributore_DTO import Distributore
from model.prezzo_DTO import Prezzo

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_tuple = []
        for distributore in self._distributori:
            conta_giorni = 0
            somma_prezzi = 0
            for prezzo in distributore.lista_prezzi:
                if prezzo.data.month == mese:
                    conta_giorni += 1
                    somma_prezzi += prezzo.prezzo_litro
            lista_tuple.append((distributore.nome, somma_prezzi/conta_giorni))
        return lista_tuple


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i.id]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if len(sequenza_parziale) == 7:
            if costo_corrente < self.__costo_ottimo or self.__costo_ottimo == -1:
                self.__sequenza_ottima = list(sequenza_parziale)
                self.__costo_ottimo = costo_corrente
            return
        else:
            for d in self._distributori:
                costo_oggi = prezzi_settimana[d.id][giorno - 1] * 100
                if ultimo_distributore is not None and d != ultimo_distributore:
                    costo_oggi += 5
                sequenza_parziale.append(d)
                self.__ricorsione(sequenza_parziale, giorno + 1, d, costo_corrente + costo_oggi, prezzi_settimana)
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        dict_prezzi_primi_giorni = {}
        for distributore in self._distributori:
            conta_giorni = 0
            dict_prezzi_primi_giorni[distributore.id] = []
            for prezzo in distributore.lista_prezzi:
                if prezzo.data.month == mese and conta_giorni < 7:
                    conta_giorni += 1
                    dict_prezzi_primi_giorni[distributore.id].append(prezzo.prezzo_litro)
        return dict_prezzi_primi_giorni