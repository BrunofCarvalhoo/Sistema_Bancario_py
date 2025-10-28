from datetime import datetime, date
from abc import ABC, abstractmethod
import textwrap

class Historico:
    def __init__(self):
        self._transacoes = []

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now()
        })

    def exibir(self, saldo):
        print("\n================ EXTRATO ================")
        if not self._transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for t in self._transacoes:
                data = t["data"].strftime("%d-%m-%Y %H:%M:%S")
                print(f"{data}\t{t['tipo']}:\tR$ {t['valor']:.2f}")
        print(f"\nSaldo:\t\tR$ {saldo:.2f}")
        print("==========================================")

    def gerar_relatorio(self, tipo_transacao=None):
        for t in self._transacoes:
            if tipo_transacao is None or t["tipo"].lower() == tipo_transacao.lower():
                yield t


class Cliente:
    def __init__(self, endereco: str):
        self._endereco = endereco
        self._contas = []

    def adicionar_conta(self, conta):
        self._contas.append(conta)

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: date, cpf: str, endereco: str):
        super().__init__(endereco)
        self._nome = nome
        self._data_nascimento = data_nascimento
        self._cpf = cpf

    @property
    def cpf(self):
        return self._cpf

    @property
    def nome(self):
        return self._nome


class Conta:
    def __init__(self, numero: int, cliente: Cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @property
    def agencia(self):
        return self._agencia

    def sacar(self, valor: float):
        if valor > 0 and self._saldo >= valor:
            self._saldo -= valor
            return True
        print("\nOperação falhou! Saldo insuficiente ou valor inválido.")
        return False

    def depositar(self, valor: float):
        if valor > 0:
            self._saldo += valor
            return True
        print("\nOperação falhou! Valor inválido.")
        return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._numero_saques = 0

    def sacar(self, valor):
        excedeu_limite = valor > self._limite
        excedeu_saques = self._numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\nOperação falhou! O valor do saque excede o limite.")
        elif excedeu_saques:
            print("\nOperação falhou! Número máximo de saques excedido.")
        elif super().sacar(valor):
            self._numero_saques += 1
            return True
        else:
            return False
        return False


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta: Conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)
            print("\nDepósito realizado com sucesso!")


class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.sacar(self._valor):
            conta.historico.adicionar_transacao(self)
            print("\nSaque realizado com sucesso!")

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


def filtrar_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None


def listar_contas(contas):
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return

    print("\n================ CONTAS ================")
    for conta in contas:
        print(f"Agência:\t{conta.agencia}") 
        print(f"C/C:\t\t{conta.numero}")
        print(f"Titular:\t{conta.cliente.nome}")
        print("-" * 40)
    print("========================================")

def main():
    clientes = []
    contas = []
    numero_conta = 1

    while True:
        opcao = menu()

        if opcao == "nu":
            cpf = input("Informe o CPF (somente número): ")
            cliente = filtrar_cliente(cpf, clientes)

            if cliente:
                print("\nJá existe cliente com esse CPF!")
                continue

            nome = input("Informe o nome completo: ")
            data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
            endereco = input("Informe o endereço: ")

            cliente = PessoaFisica(nome, datetime.strptime(data_nascimento, "%d-%m-%Y").date(), cpf, endereco)
            clientes.append(cliente)
            print("\nCliente criado com sucesso!")

        elif opcao == "nc":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nCliente não encontrado!")
                continue

            conta = ContaCorrente(numero_conta, cliente)
            cliente.adicionar_conta(conta)
            contas.append(conta)
            numero_conta += 1
            print("\nConta criada com sucesso!")

        elif opcao == "d":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nCliente não encontrado!")
                continue

            if not cliente._contas:
                print("\nCliente não possui conta! Crie uma conta primeiro.")
                continue

            conta = cliente._contas[0] 

            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(conta, transacao) 

        elif opcao == "s":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nCliente não encontrado!")
                continue

            if not cliente._contas:
                print("\nCliente não possui conta! Crie uma conta primeiro.")
                continue

            conta = cliente._contas[0]

            valor = float(input("Informe o valor do saque: "))
            transacao = Saque(valor)
            cliente.realizar_transacao(conta, transacao) 

        elif opcao == "e":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nCliente não encontrado!")
                continue

            if not cliente._contas:
                print("\nCliente não possui conta! Crie uma conta primeiro.")
                continue
            
            conta = cliente._contas[0] 
            conta.historico.exibir(conta.saldo)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "r":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nCliente não encontrado!")
                continue

            if not cliente._contas:
                print("\nCliente não possui conta! Crie uma conta primeiro.")
                continue

            conta = cliente._contas[0]

            tipo = input("Filtrar por tipo (d=depósito, s=saque, [enter]=todas): ").lower()
            tipo_filtro = None
            if tipo == 'd':
                tipo_filtro = 'deposito'
            elif tipo == 's':
                tipo_filtro = 'saque'

            print(f"\n===== RELATÓRIO DE TRANSAÇÕES ({tipo_filtro or 'Todas'}) =====")
            relatorio = conta.historico.gerar_relatorio(tipo_transacao=tipo_filtro)
            transacoes_encontradas = False
            for t in relatorio:
                transacoes_encontradas = True
                data = t["data"].strftime("%d-%m-%Y %H:%M:%S")
                print(f"{data}\t{t['tipo']}:\tR$ {t['valor']:.2f}")
            if not transacoes_encontradas:
                print("Nenhuma transação encontrada.")
            print("==================================================")

        elif opcao == "q":
            print("\nSaindo do sistema...")
            break

        else:
            print("\nOpção inválida!")


if __name__ == "__main__":
    main()