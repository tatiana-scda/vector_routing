import sys, json, random, socket, ipaddress, time

def tempoAtualizacao():
    if (len(sys.argv) == 3): float(sys.argv[2])
    else: 3.0

TEMPO_ATUALIZACAO = tempoAtualizacao()
TEMPO_EXPIRACAO   = 4*TEMPO_ATUALIZACAO
STARTUP           = None
# tempo de expiracao determinado pelo professor


def atualizaTabelaDistancias(tabela_distancias):
# atualiza a tabela, para ignorar os roteadores que expiraram!
    copia_tabela_distancias = {}
    for destino, roteador_infos in tabela_distancias.items():
        for roteador_vizinho, lista_peso_tempo in roteador_infos.items():
            if time.time() - lista_peso_tempo[1] <= TEMPO_EXPIRACAO:
                # ou seja, se ele nao expirou, logo continuara na tabela de distancias apos esta atualizacao
                copia_tabela_distancias[destino][roteador_vizinho] = lista_peso_tempo
    tabela_distancias = copia_tabela_distancias


class TabelaDeDistancias:
    # tabela de roteamento para roteadores que o Roteador nao conhece (sem diretos).
    # formato: a tabela eh um dicionario, sendo key o ip do destino, value um dicionario que contem como key o roteador
    # vizinho, e value uma lista [peso, tempo_expiracao]

    def __init__(self, endereco_ip):
        # cada tabela de distancias guarda o endereco ip do roteador que instancia sua tabela e um dict de dicts (que
        # sao os destinos e seus pesos, alem do timeout para expiracao).
        self.endereco_ip       = endereco_ip
        self.tabela_distancias = {}

    def saltoDeRoteador(self, roteador_destino):
        # anda em direcao ao destino; uma nova tabela eh gerada sempre que acontece o salto, pois se algum roteador for
        # deletado por expirar, ele nao sera considerado mais na tabela de distancias do roteador instanciado!
        global TEMPO_EXPIRACAO
        atualizaTabelaDistancias(self.tabela_distancias)

        # para destinos contidos na tabela com valores de pesos minimos tambem iguais, faz-se uma selecao balanceada de
        # qual pulo realizara para que, estatisticamente, ao final das contas, seja sempre mais ou menos 50%, sem
        # preferencia por alguma das rotas.
        if roteador_destino in self.tabela_distancias:
            caminho_curto = self.tabela_distancias[roteador_destino]
            for destino, roteador_infos in self.tabela_distancias.items():
                for roteador_vizinho, lista_peso_tempo in roteador_infos.items():
                    if lista_peso_tempo[0] < caminho_curto:
                        caminho_curto = lista_peso_tempo[0]

class Roteador:
    pass

class Entrada:
    def __init__(self, roteador):
        self.roteador = roteador

    def comandoAdd(self, comando):
        funcao, vizinho, peso = comando.split()
        try:
            vizinho = ipaddress.IPv4Address(vizinho)
            # validando se a string eh ip valido.

            vizinho = str(vizinho)
            peso    = int(peso)

        except ValueError:
            return


    def comandoDel(self, comando):
        funcao, vizinho = comando.split()
        pass

    def comandoTrace(self, comando):
        funcao, destino = comando.split()
        pass

    def lerEntrada(self):
        # leitura da linha do terminal, apos isso, define-se qual comando será executado seguindo o começo deste comando.
        comando = sys.stdin.readline()
        funcao  = comando.split()[0]

        # de acordo com o comando, direciona para a função do comando.
        if funcao   == 'add':
            comandoAdd(comando)
        elif funcao == 'del':
            comandoDel(comando)
        elif funcao == 'trace':
            comandoTrace(comando)

def main():
    Entrada()

if __name__ == '__main__':
    main()