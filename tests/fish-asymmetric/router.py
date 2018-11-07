import sys, json, random, socket, ipaddress, time, selectors

if (len(sys.argv) == 3):
    TEMPO_ATUALIZACAO = float(sys.argv[2])
TEMPO_ATUALIZACAO = 3.0
TEMPO_EXPIRACAO   = 4*TEMPO_ATUALIZACAO

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

    def processar_mensagem(self, mensagem, roteador_destino):
        for roteador_destino in self.tabela_distancias:
            
            # lulis posso fazer isso aqui?
            # slip horizon
            if (roteador_destino != self.ip_endereco):
                self.socket.sendto(mensagem.encode('utf-8'), (roteador_destino, self.port)) 


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
            return roteador_escolhido
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

    def processaTrace(self, mensagem):
        # construcao da proxima mensagem por meio da que temos, com o ip do atual roteador.
        origem = mensagem['source']
        destino = mensagem['destination']
        mensagem['hops'].append(self.roteador.ip_endereco)

        # confirma se este roteador eh o enderecado como destino. se o roteador for o destino do trace, ele deve enviar
        # uma mensagem data para o roteador que originou o trace; o payload da mensagem data deve ser um string contendo
        # o JSON correspondente à mensagem de trace.
        if self.ip_endereco == destino:
            payload = json.dumps(mensagem)
            mensagem = {
                'type': 'data',
                'source': self.ip_endereco,
                'destination': origem,
                'payload': payload
            }
        self.saltar_roteador(mensagem)

    def processaAtualizacao(self, mensagem):
        roteador_vizinho = mensagem['origem']
        dicionario_melhores_distancias = mensagem['distances']

        dicionario_melhores_distancias.pop(self.ip_endereco)
        for destino, distancia in dicionario_melhores_distancias.items():
            lista_peso_tempo = [distancia + self.tabela_distancias.tabela_distancias[roteador_vizinho], time.time()]
            self.tabela_distancias.tabela_distancias[destino][roteador_vizinho] = lista_peso_tempo

    def processa_mensagem(self):
        # esta funcao eh de callback para cada mensagem que chegar no socket.
        msg, endereco     = self.socket.recvfrom(65535)
        ip_vizinho, porto = endereco
        mensagem          = json.loads(msg.decode('utf-8'))

        if mensagem['type'] == 'data':
        # se for 'data', ele tem que repassar a data para o proximo roteador vizinho em direcao ao destino dela.
            self.saltar_roteador(mensagem)
        if mensagem['type'] == 'trace':
        # se ele for 'trace', ele tem que andar para o proximo vizinho em direcao ao destino.
            processaTrace(mensagem)
        if mensagem['type'] == 'update':
        # se ele for 'update', tem que atualizar sua tabela de distancias forcadamente.
            processaAtualizacao(mensagem)

    def saltar_roteador(self, msg):
        mensagem = json.dumps(msg)
        destino  = msg['destination']

        if destino != self.addr:
            roteador_vizinho = self.tabela_distancias.saltoDeRoteador(destino)
            if roteador_vizinho is None: return
            self.socket.sendto(mensagem.encode('utf-8'), (roteador_vizinho, self.porto))

    def atualiza_vizinhos(self, ip_roteador_vizinho):
        global TEMPO_EXPIRACAO
        dicionario_melhores_distancias = {}

        atualizaTabelaDistancias(self.tabela_distancias.tabela_distancias)
        dicionario_melhores_distancias[self.ip_endereco] = 0

        for destino, dict_roteadores in self.tabela_distancias.tabela_distancias.items():
            if destino == ip_roteador_vizinho:
                continue
            entradas = list((entrada for h, entrada in dict_roteadores.items() if h != ip_roteador_vizinho))
            if entradas:
                dicionario_melhores_distancias[destino] = min(entrada.distancia for entrada in entradas)

        mensagem = {
            'type': 'update',
            'source': self.ip_endereco,
            'destination': ip_roteador_vizinho,
            'distances': dicionario_melhores_distancias
        }

        mensagem_string = json.dumps(mensagem, indent=2)
        self.socket.sendto(mensagem_string.encode('utf-8'), (ip_roteador_vizinho, self.porto))

class ComandosDeEntrada:
    # roteador eh instanciado.
    def __init__(self, roteador):
        self.roteador = roteador

    def comandoAdd(self, ip_roteador_vizinho, peso):
        ip_roteador_vizinho            = str(ip_roteador_vizinho)
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
        # construcao da proxima mensagem por meio da que temos, com o ip do atual roteador.
        origem  = mensagem['source']
        destino = mensagem['destination']
        mensagem['hops'].append(self.roteador.ip_endereco)

        # confirma se este roteador eh o enderecado como destino. se o roteador for o destino do trace, ele deve enviar
        # uma mensagem data para o roteador que originou o trace; o payload da mensagem data deve ser um string contendo
        # o JSON correspondente à mensagem de trace.
        if self.roteador.ip_endereco == destino:
            payload = json.dumps(mensagem)
            mensagem = {
                'type': 'data',
                'source': self.roteador.ip_endereco,
                'destination': origem,
                'payload': payload
            }
        self.roteador.saltar_roteador(mensagem)

    def processa_comando(self, linha=None):
        # leitura da linha do terminal, apos isso, define-se qual comando será executado seguindo o começo deste comando
        if linha != None:
            comando = linha
        else:
            comando = sys.stdin.readline()

        funcao  = comando.split()[0]

        # de acordo com o comando, direciona para a função do comando.
        if funcao   == 'add':
            self.comandoAdd(comando.split()[1], comando.split()[2])

        elif funcao == 'del':
            self.comandoDel(comando.split()[1])

        elif funcao == 'trace':
            ip_roteador_destino = comando.split()[1]

            mensagem = {
                "type": "trace",
                "source": self.roteador.ip_endereco,
                "destination": ip_roteador_destino,
                "hops": []
            }
            self.comandoTrace(mensagem)

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
    selectors.DefaultSelector().register(sys.stdin,       selectors.EVENT_READ, comandos_de_entrada.processa_comando)
    selectors.DefaultSelector().register(roteador.socket, selectors.EVENT_READ, roteador.processa_mensagem)

    proximo_update = time.time() + TEMPO_ATUALIZACAO
    

    while True:
        tempo_restante = proximo_update - time.time()
        if tempo_restante <= 0:
            for roteador_vizinho in roteador.tabela_distancias.tabela_distancias:
                roteador.atualiza_vizinhos(roteador_vizinho)
            proximo_update = proximo_update + TEMPO_ATUALIZACAO
        ioStream = selector.select(timeout=tempo_restante)
        for chave, mascara in ioStream:
            callback = chave.data
            callback()

    selector.close()

if __name__ == '__main__':
    main()