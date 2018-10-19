import sys, json, random, socket, ipaddress, time, selectors

TEMPO_ATUALIZACAO = sys.argv[2]

def atualizaTabelaDistancias(tabela_distancias):
# atualiza a tabela, para ignorar os roteadores que expiraram!
    copia_tabela_distancias = {}
    for destino, dict_roteadores in tabela_distancias.items():
        for roteador_vizinho, lista_peso_tempo in dict_roteadores.items():
            if time.time() - lista_peso_tempo[1] <= TEMPO_EXPIRACAO:
                # ou seja, se ele nao expirou, logo continuara na tabela de distancias apos esta atualizacao
                copia_tabela_distancias[destino][roteador_vizinho] = lista_peso_tempo
    tabela_distancias = copia_tabela_distancias


class TabelaDeDistancias:
    # tabela de roteamento para roteadores que o Roteador nao conhece (sem diretos).
    # formato: a tabela eh um dicionario, sendo key o ip do destino, value um dicionario que contem como key o roteador
    # vizinho, e value uma lista [peso, tempo_expiracao]
    #  { ip_destino : { ip_roteador_vizinho : [ peso, tempo_expiracao ] }}

    def __init__(self, endereco_ip):
        # cada tabela de distancias guarda o endereco ip do roteador que instancia sua tabela e um dict de dicts (que
        # sao os destinos e seus pesos, alem do timeout para expiracao).
        self.endereco_ip       = endereco_ip
        self.tabela_distancias = {}

    def saltoDeRoteador(self, roteador_destino):
        # anda em direcao ao destino; uma nova tabela eh gerada sempre que acontece o salto, pois se algum roteador for
        # deletado por expirar, ele não será considerado mais na tabela de distancias do roteador instanciado!
        global TEMPO_EXPIRACAO
        atualizaTabelaDistancias(self.tabela_distancias)

        if roteador_destino in self.tabela_distancias:
            caminho_minimo = min(dict_roteadores[1] for dict_roteadores in self.tabela_distancias[roteador_destino].values())

            # para destinos contidos na tabela com valores de pesos minimos tambem iguais, faz-se uma selecao balanceada de
            # qual pulo realizara para que, estatisticamente, ao final das contas, seja sempre mais ou menos 50%, sem
            # preferencia por alguma das rotas.
            lista_roteadores_minimos = []
            for roteador_vizinho in self.tabela_distancias[roteador_destino].items():
                if self.tabela_distancias[roteador_destino][roteador_vizinho][1] == caminho_minimo:
                    lista_roteadores_minimos.append(roteador_vizinho)

            roteador_escolhido = random.choice(lista_roteadores_minimos)
        else:
            # o destino não está na lista de destinos alcançáveis pelo roteador, através da tabela de distâncias.
            return

class Roteador:
    def __init__(self, ip_endereco, porto):
        # cria conexao socket para o roteador instanciado  a partir do endereco de ip e do porto definido para ele.
        self.ip_endereco = ip_endereco
        self.porto       = porto
        self.socket      = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.socket.bind((self.ip_endereco, self.porto))

        # cada roteador precisa de ter sua tabela de distancias entre o destino e ele mesmo, todos os quais são alcançáveis
        # por meio de algum roteador vizinho. Para tal, cada roteador instancia uma TabelaDeDistancias. Também é necessário
        # ter um dict de roteadores vizinhos, para guardar a referência dos roteadores vizinhos e o peso ate chegar a eles.
        self.tabela_distancias             = TabelaDeDistancias(self.ip_endereco)
        self.distancia_roteadores_vizinhos = {}

### >>>>>>>>>>>>>> FALTA IMPLEMENTAR PROCESSAR MENSAGEM <<<<<<<<<<<<<<<< ###
# o que falta: ver o tipo da mensagem
# se for update, ele tem que updatar sua tabela de distancias, tem funcao LA EM CIMA de update, conferir!!! so chamar talvez, n sei se eh a mesma ideia.
# se for trace, ele tem que se gravar no trace e repassar pra frente a caminho do destino
# se for data, ele tem que repassar a data para o prox roteador vizinho em direcao ao destino dela. ou receber, se for dele.
# andre cria uma funcao route que significa repassar para o proximo vizinho a caminho do destino, usado em trace e data.
# ele tb define uma funcao chamada send_update, que empacota a sua tabela atualizada (tem funcao disso ja em, so chamar talvez, n sei se eh a mesma ideia). tambem cria uma msg data e envia pros vizinhos

        def processar_mensagem(self):
            pass

class ComandosDeEntrada:
### >>>>>>>>>>>>>> FALTA IMPLEMENTAR OS COMANDOS <<<<<<<<<<<<<<<< ###

    def __init__(self, roteador):
        self.roteador = roteador

    def comandoAdd(self, comando):
        funcao, roteador_vizinho, peso = comando.split()
        roteador_vizinho               = str(vizinho)
        peso                           = int(peso)

    def comandoDel(self, comando):
        funcao, vizinho = comando.split()
        
        for destino, dict_roteadores in tabela_distancias.items():
            caminho.remove(dict_roteadores)

    def comandoTrace(self, comando):
        funcao, destino = comando.split()
        # se houver caminho valido
        if (saltoDeRoteador(self, destino)):
            caminho = list()

        # passa por todos roteadores no caminho e adiciona em uma lista
        for destino, dict_roteadores in tabela_distancias.items():
            caminho.append(dict_roteadores)
        
        mensagem = {
            "type": "trace"
            "source": self.ip_endereco
            "destination": destino
            "payload": caminho
        }
        

    def processa_comando(self):
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
    ### INICIALIZACAO DO ROTEADOR ###
    endereco_ip       = str(sys.argv[1])
    porto             = 55151
    STARTUP           = None
    selector          = selectors.DefaultSelector()

    # instancio um Roteador para este programa
    roteador            = Roteador(endereco_ip, porto)

    # instancio um gerenciador de Comandos de Entrada (sejam eventos que ocorrem no stdin,
    comandos_de_entrada = ComandosDeEntrada(roteador)

    # no caso do argumento STARTUP ser setado, leremos os comandos a partir do arquivo dado de input neste argumento.
    if len(sys.argv) == 4 and sys.argv[3] != None:
        arquivo = open(sys.argv[3], 'r')
        for linha in arquivo:
            comandos_de_entrada.processa_comando(linha)

    # monitoramento de eventos I/O para os objetos registrados & monitoramento de qualquer mensagem que chegar no socket
    selectors.DefaultSelector().register(sys.stdin,     sekectors.EVENT_READ, comandos_de_entrada.processa_comando)
    selectors.DefaultSelector().register(router.socket, sekectors.EVENT_READ, router.processa_mensagem)

### >>>>>>>>>>>>>> FALTA IMPLEMENTAR A UPDATE COM TIMEOUT <<<<<<<<<<<<<<<< ###

    selector.close()

if __name__ == '__main__':
    main()