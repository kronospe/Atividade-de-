from dataclasses import dataclass

@dataclass
class Endereco:
    rua: str
    numero: str
    cidade: str
    uf: str
    cep: str

    def e_valido(self) -> bool:
        return self.cep is not None and len(self.cep.replace("-", "")) == 8

    def formatar(self) -> str:
        return f"{self.rua}, {self.numero}, {self.cidade}/{self.uf}, CEP {self.cep}"


@dataclass
class Cliente:
    nome: str
    email: str
    tipo: str

    def validar(self) -> str | None:
        if self.nome is None or self.nome.strip() == "":
            return "ERRO: cliente sem nome"
        if self.email is None or "@" not in self.email or "." not in self.email:
            return "ERRO: email invalido"
        return None


class ItemPedido:
    def __init__(self, produto: str, quantidade: int, preco: float):
        self.produto = produto
        self.quantidade = int(quantidade)
        self.preco = float(preco)

    def subtotal(self) -> float:
        return self.quantidade * self.preco


class ServicoEstoque:
    def __init__(self, estoque_inicial=None):
        self._estoque = estoque_inicial or {"CANETA": 100, "CADERNO": 50, "MOCHILA": 10, "CALCULADORA": 5}

    def __getitem__(self, item):
        return self._estoque[item]

    def __setitem__(self, key, value):
        self._estoque[key] = value

    def __contains__(self, item):
        return item in self._estoque

    def verificar_disponibilidade(self, produto: str, quantidade: int) -> str | None:
        if produto not in self._estoque:
            return f"ERRO: produto inexistente {produto}"
        if self._estoque[produto] < quantidade:
            return f"ERRO: estoque insuficiente {produto}"
        return None

    def baixar(self, produto: str, quantidade: int):
        self._estoque[produto] -= quantidade

    def verificar_alertas(self) -> str:
        alerta = ""
        for produto, qtd in self._estoque.items():
            if qtd < 5:
                alerta += f"ALERTA: {produto} com estoque baixo ({qtd})\n"
                print(f"[EMAIL para compras@loja.com] Repor {produto}")
        return alerta


class RepositorioPedidos:
    @staticmethod
    def salvar_csv(cliente: Cliente, pagamento: str, total: float, endereco_str: str):
        try:
            with open("pedidos.csv", "a", encoding="utf-8") as f:
                f.write(f"{cliente.nome};{cliente.email};{cliente.tipo};{pagamento};{total};{endereco_str}\n")
        except OSError as e:
            print("Falha ao salvar pedido: " + str(e))


class ServicoNotificacao:
    @staticmethod
    def enviar_confirmacao(cliente: Cliente, total: float, endereco_str: str):
        mensagem = f"Ola {cliente.nome}, seu pedido foi confirmado. "
        if cliente.tipo == "VIP":
            mensagem += "Obrigado por ser VIP! Frete gratis garantido. "
        elif cliente.tipo == "FUNCIONARIO":
            mensagem += "Desconto de colaborador aplicado. "
        mensagem += f"Total: R$ {total:.2f}. Entrega em: {endereco_str}"
        print(f"[EMAIL para {cliente.email}] {mensagem}")


class CalculadoraDesconto:
    @staticmethod
    def calcular(subtotal: float, tipo_cliente: str) -> float:
        if tipo_cliente == "COMUM":
            return subtotal * 0.05 if subtotal > 500 else 0.0
        elif tipo_cliente == "VIP":
            return subtotal * 0.15 if subtotal > 500 else subtotal * 0.10
        elif tipo_cliente == "FUNCIONARIO":
            return subtotal * 0.20
        return -1.0


class CalculadoraFrete:
    ESTADOS_NE = {"PB", "AL", "RN", "BA", "SE", "CE", "PI", "MA"}

    @classmethod
    def calcular(cls, uf: str, subtotal_com_desconto: float, tipo_cliente: str) -> float:
        if subtotal_com_desconto > 300 or tipo_cliente == "VIP":
            return 0.0
        if uf == "PE":
            return 12.50
        elif uf in cls.ESTADOS_NE:
            return 22.90
        return 39.90


class CalculadoraPagamento:
    @staticmethod
    def aplicar(total: float, pagamento: str, parcelas: int):
        if pagamento == "PIX":
            return total * 0.95
        elif pagamento == "BOLETO":
            return total + 2.5
        elif pagamento == "CARTAO":
            if parcelas < 1 or parcelas > 12:
                return None
            if parcelas > 3:
                return total * (1 + 0.0199 * parcelas)
            return total
        return None


class GeradorRelatorio:
    @staticmethod
    def gerar(historico: list, total_vendido: float) -> str:
        r = "=== RELATORIO DE VENDAS ===\n"
        vip = comum = func = 0
        for h in historico:
            partes = h.split("|")
            if partes[1] == "VIP":
                vip += 1
            elif partes[1] == "COMUM":
                comum += 1
            elif partes[1] == "FUNCIONARIO":
                func += 1
            r += f"{partes[0]} ({partes[1]}): R$ {float(partes[2]):.2f}\n"
        r += f"Pedidos VIP: {vip}\nPedidos COMUM: {comum}\nPedidos FUNCIONARIO: {func}\n"
        r += f"Total vendido: R$ {total_vendido:.2f}\n"
        if total_vendido > 10000:
            r += "Meta mensal atingida!\n"
        return r


class GerenciadorPedidos:
    def __init__(self):
        self.itens = []
        self.estoque = ServicoEstoque()
        self.historico = []
        self.total_vendido = 0

    def adicionar_item(self, produto, qtd, preco):
        self.itens.append(ItemPedido(produto, qtd, preco))

    def processar_pedido(self, nome, email, tipo_cliente, pagamento, parcelas,
                         rua, numero, cidade, uf, cep):
        cliente = Cliente(nome, email, tipo_cliente)
        erro_cliente = cliente.validar()
        if erro_cliente:
            return erro_cliente

        if len(self.itens) == 0:
            return "ERRO: pedido vazio"

        endereco = Endereco(rua, numero, cidade, uf, cep)
        if not endereco.e_valido():
            return "ERRO: cep invalido"

        for item in self.itens:
            erro_estoque = self.estoque.verificar_disponibilidade(item.produto, item.quantidade)
            if erro_estoque:
                return erro_estoque

        subtotal = sum(item.subtotal() for item in self.itens)
        desconto = CalculadoraDesconto.calcular(subtotal, cliente.tipo)
        if desconto < 0:
            return "ERRO: tipo de cliente desconhecido"

        frete = CalculadoraFrete.calcular(endereco.uf, subtotal - desconto, cliente.tipo)
        total_parcial = subtotal - desconto + frete

        total = CalculadoraPagamento.aplicar(total_parcial, pagamento, parcelas)
        if total is None:
            if pagamento == "CARTAO":
                return "ERRO: parcelas invalidas"
            return "ERRO: forma de pagamento invalida"

        total = round(total * 100.0) / 100.0

        for item in self.itens:
            self.estoque.baixar(item.produto, item.quantidade)

        str_endereco = endereco.formatar()

        RepositorioPedidos.salvar_csv(cliente, pagamento, total, str_endereco)
        ServicoNotificacao.enviar_confirmacao(cliente, total, str_endereco)

        self.historico.append(f"{cliente.nome}|{cliente.tipo}|{total}")
        self.total_vendido += total
        self.itens.clear()
        return f"OK: {total:.2f}"

    def calcular_orcamento(self, tipo_cliente, uf):
        subtotal = sum(item.subtotal() for item in self.itens)
        desconto = CalculadoraDesconto.calcular(subtotal, tipo_cliente)
        if desconto < 0:
            desconto = 0
        frete = CalculadoraFrete.calcular(uf, subtotal - desconto, tipo_cliente)
        return round((subtotal - desconto + frete) * 100.0) / 100.0

    def gerar_relatorio(self):
        return GeradorRelatorio.gerar(self.historico, self.total_vendido)

    def verificar_estoque(self):
        return self.estoque.verificar_alertas()

    def mensagem_promocional(self, tipo_cliente):
        if tipo_cliente == "VIP":
            return "Ofertas exclusivas: 15% em compras acima de R$ 500!"
        elif tipo_cliente == "COMUM":
            return "Compre acima de R$ 500 e ganhe 5% de desconto!"
        elif tipo_cliente == "FUNCIONARIO":
            return "Lembrete: seu desconto de 20% vale em toda a loja."
        return ""