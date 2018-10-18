import sys, json, random, socket

def comandoAdd(comando):
    funcao, vizinho, peso = comando.split()
    print(funcao, vizinho, peso)

def comandoDel(comando):
    funcao, vizinho = comando.split()
    pass

def comandoTrace(comando):
    funcao, destino = comando.split()
    pass

def lerEntrada():
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
    lerEntrada()

if __name__ == '__main__':
    main()