import textwrap
from datetime import datetime

def log_transacao(func):
    
    def wrapper(*args, **kwargs):
        
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        args_str = f"args={args!r}, kwargs={kwargs!r}"

        try:
           
            resultado = func(*args, **kwargs)
            retorno_str = repr(resultado) 
            
            log_entry = f"[{agora}] Função: {func.__name__} | Argumentos: {args_str} | Retorno: {retorno_str}\n"

        except Exception as e:
            
            retorno_str = f"Exceção: {e!r}"
            log_entry = f"[{agora}] Função: {func.__name__} | Argumentos: {args_str} | Retorno: {retorno_str}\n"
            
            try:    
                with open("log.txt", "a", encoding="utf-8") as f:
                    f.write(log_entry)
            except Exception as log_e:
                
                print(f"ERRO CRÍTICO: Falha ao escrever log de ERRO no arquivo: {log_e}")

            raise e 
        try:
            
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as log_e:
            
            print(f"Falha ao escrever log de SUCESSO no arquivo: {log_e}")
            print(f"Log que falhou: {log_entry}")
            
        
        return resultado
    
    return wrapper


def menu():
    menu_texto = """
    Opções:
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [r]\tRelatório de Transações
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_texto))

@log_transacao
def depositar(saldo, valor, historico, /):
    
    if valor > 0:
        saldo += valor
        
        historico.append({
            "tipo": "Depósito",
            "valor": valor,
            "data": datetime.now()
        })
        print("\nDepósito realizado com sucesso!")
    else:
        print("\nOperação falhou! O valor informado é inválido.")

    return saldo, historico

@log_transacao
def sacar(*, saldo, valor, historico, limite, numero_saques, limite_saques):
   
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("\n Operação falhou! Você não tem saldo suficiente.")
    elif excedeu_limite:
        print("\n Operação falhou! O valor do saque excede o limite. ")
    elif excedeu_saques:
        print("\n Operação falhou! Número máximo de saques excedido. ")
    elif valor > 0:
        saldo -= valor
        
        historico.append({
            "tipo": "Saque",
            "valor": valor,
            "data": datetime.now()
        })
        numero_saques += 1
        print("\nSaque realizado com sucesso!")
    else:
        print("\n Operação falhou! O valor informado é inválido.")

    return saldo, historico, numero_saques


def exibir_extrato(saldo, /, *, historico):
 
    print("\n================ EXTRATO ================")
    if not historico:
        print("Não foram realizadas movimentações.")
    else:
        
        for transacao in historico:
            data_formatada = transacao["data"].strftime("%d-%m-%Y %H:%M:%S")
            print(f"{data_formatada}\t{transacao['tipo']}:\tR$ {transacao['valor']:.2f}")

    print(f"\nSaldo:\t\tR$ {saldo:.2f}")
    print("==========================================")



def gerar_relatorio_transacoes(historico, *, tipo_transacao=None):
  
    for transacao in historico:
        if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
            yield transacao


@log_transacao
def criar_usuario(usuarios):
 
    cpf = input("Informe o CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\nJá existe usuário com esse CPF!")
        return 

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})

    print("Usuário criado com sucesso!")


def filtrar_usuario(cpf, usuarios):
   
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


@log_transacao
def criar_conta(agencia, numero_conta, usuarios, contas):
   
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        contas.append({"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario})
        print("\n=== Conta criada com sucesso! ===")
        return numero_conta + 1 
    
    print("\nUsuário não encontrado, fluxo de criação de conta encerrado!")
    return numero_conta 



class ContaIterador:
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
       
        if self._index >= len(self._contas):
            raise StopIteration
        
        conta = self._contas[self._index]
        self._index += 1
        
        info = f"""\
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
        """
        return info


def listar_contas(contas):
  
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return

    print("\n================ CONTAS ================")
    
    for conta_info in ContaIterador(contas):
        print(textwrap.dedent(conta_info))
        print("-" * 40)
    print("========================================")


def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"

    saldo = 0
    limite = 500
    historico = [] 
    numero_saques = 0
    usuarios = []
    contas = []
    numero_conta = 1

    while True:
        opcao = menu()

        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            
            saldo, historico = depositar(saldo, valor, historico)

        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))

            saldo, historico, numero_saques = sacar(
                saldo=saldo,
                valor=valor,
                historico=historico,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
            )

        elif opcao == "e":
            
            exibir_extrato(saldo, historico=historico)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = criar_conta(AGENCIA, numero_conta, usuarios, contas)

        elif opcao == "lc":
            listar_contas(contas)

        
        elif opcao == "r":
            tipo = input("Filtrar por tipo (d=depósito, s=saque, [enter]=todas): ").lower()
            tipo_filtro = None
            if tipo == 'd':
                tipo_filtro = 'depósito'
            elif tipo == 's':
                tipo_filtro = 'saque'
            
            print(f"\n===== RELATÓRIO DE TRANSAÇÕES ({tipo_filtro or 'Todas'}) =====")
            
            
            relatorio = gerar_relatorio_transacoes(historico, tipo_transacao=tipo_filtro)
            transacoes_encontradas = False
            for transacao in relatorio:
                transacoes_encontradas = True
                data_formatada = transacao["data"].strftime("%d-%m-%Y %H:%M:%S")
                print(f"{data_formatada}\t{transacao['tipo']}:\tR$ {transacao['valor']:.2f}")
            
            if not transacoes_encontradas:
                print("Nenhuma transação encontrada para este filtro.")
            print("==================================================")

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


if __name__ == "__main__":
    main()