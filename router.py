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

    def processar_mensagem(self, mensagem):
        for roteador in self.tabela_distancias:
            # lulis posso fazer isso aqui?
            # slip horizon
            if (roteador != self.ip_endereco):
                self.socket.sendto(mensagem.encode('utf-8'), (destino, self.port)) 


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
    def enviar(self, mensagem):


class ComandosDeEntrada:
    # roteador eh instanciado.
    def __init__(self, roteador):
        self.roteador = roteador

    def comandoAdd(self, ip_roteador_vizinho, peso):
        ip_roteador_vizinho               = str(ip_roteador_vizinho)
        peso                           = int(peso)

        # insere este novo enlace virtual entre o roteador corrente e o roteador associado ao endereço ip dado.
        self.roteador.distancia_roteadores_vizinhos[ip_roteador_vizinho] = peso

        # como atualizamos a tabela, enviamos um update para a rede como broadcast.
        self.roteador.atualiza_vizinhos(ip_roteador_vizinho)

    def comandoDel(self, ip_roteador_vizinho):
        ip_roteador_vizinho               = str(ip_roteador_vizinho)

        # deleta o roteador do dict distancia_roteadores_vizinhos usando seu ip e atualiza a tabela de distancias.
        if self.roteador.distancia_roteadores_vizinhos.get(ip_roteador_vizinho):
            self.roteador.distancia_roteadores_vizinhos.pop(ip_roteador_vizinho)

        copia_tabela_distancias = {}
        for destino, dict_roteadores in self.roteador.tabela_distancias.items():
            for roteador_vizinho, lista_peso_tempo in dict_roteadores.items():
                if roteador_vizinho != ip_roteador_vizinho:
                    dict_roteadores[roteador_vizinho] = lista_peso_tempo
                else:
                    return
        self.roteador.tabela_distancias = copia_tabela_distancias

    def comandoTrace(self, ip_roteador_destino, mensagem):
        ip_roteador_vizinho = str(ip_roteador_destino)

        # construcao da proxima mensagem por meio da que temos, com o ip do atual roteador.
        origem  = mensagem['source']
        destino = mensagem['destination']
        mensagem['hops'].append(self.roteador.ip_endereco)

        # confirma se este roteador eh o enderecado como destino. se o roteador for o destino do trace, ele deve enviar
        # uma mensagem data para o roteador que originou o trace; o payload da mensagem data deve ser um string contendo
        # o JSON correspondente à mensagem de trace.
        if self.roteador.ip_endereco == ip_roteador_destino:
            payload = json.dumps(mensagem)
            mensagem = {
                'type': 'data',
                'source': self.roteador.ip_endereco,
                'destination': origem,
                'payload': payload
            }

        self.roteador.enviar(mensagem)

        
    def processa_comando(self):
        # leitura da linha do terminal, apos isso, define-se qual comando será executado seguindo o começo deste comando.
        comando = sys.stdin.readline()
        funcao  = comando.split()[0]

        # de acordo com o comando, direciona para a função do comando.
        if funcao   == 'add':
            comandoAdd(comando.split()[1], comando.split()[2])

        elif funcao == 'del':
            comandoDel(comando.split()[1])

        elif funcao == 'trace':
            ip_roteador_destino = comando.split()[1]

            mensagem = {
                "type": "trace",
                "source": self.roteador.ip_endereco,
                "destination": ip_roteador_destino,
                "hops": []
            }

            comandoTrace(ip_roteador_destino, mensagem)

        else:
            sys.exit(1)

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