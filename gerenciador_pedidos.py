class ItemPedido:
    def __init__(self, produto: str, quantidade: int, preco: float):
        self.produto = produto
        self.quantidade = int(quantidade)
        self.preco = float(preco)

    def subtotal(self) -> float:
        return self.quantidade * self.preco

class CalculadoraDesconto:
    @staticmethod
    def calcular(subtotal: float, tipo_cliente: str) -> float:
        if tipo_cliente == "COMUM":
            return subtotal * 0.05 if subtotal > 500 else 0.0
        elif tipo_cliente == "VIP":
            return subtotal * 0.15 if subtotal > 500 else subtotal * 0.10
        elif tipo_cliente == "FUNCIONARIO":
            return subtotal * 0.20
        return -1.0  # Código de tipo de cliente desconhecido


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

class GerenciadorPedidos:
    def __init__(self):
        self.itens = []
        self.estoque = {"CANETA": 100, "CADERNO": 50, "MOCHILA": 10, "CALCULADORA": 5}
        self.historico = []
        self.total_vendido = 0
        
    def adicionar_item(self, produto, qtd, preco):
        self.itens.append(ItemPedido(produto, qtd, preco))

    def processar_pedido(self, nome, email, tipo_cliente, pagamento, parcelas,
                         rua, numero, cidade, uf, cep):
        if nome is None or nome.strip() == "":
            return "ERRO: cliente sem nome"
        if email is None or "@" not in email or "." not in email:
            return "ERRO: email invalido"
        if len(self.itens) == 0:
            return "ERRO: pedido vazio"
        if cep is None or len(cep.replace("-", "")) != 8:
            return "ERRO: cep invalido"

        for item in self.itens:
            if item.produto not in self.estoque:
                return f"ERRO: produto inexistente {item.produto}"
            if self.estoque[item.produto] < item.quantidade:
                return f"ERRO: estoque insuficiente {item.produto}"

        subtotal = sum(item.subtotal() for item in self.itens)
        desconto = CalculadoraDesconto.calcular(subtotal, tipo_cliente)
        if desconto < 0:
            return "ERRO: tipo de cliente desconhecido"

        frete = CalculadoraFrete.calcular(uf, subtotal - desconto, tipo_cliente)
        total_parcial = subtotal - desconto + frete

        total = CalculadoraPagamento.aplicar(total_parcial, pagamento, parcelas)
        if total is None:
            if pagamento == "CARTAO":
                return "ERRO: parcelas invalidas"
            return "ERRO: forma de pagamento invalida"

        total = round(total * 100.0) / 100.0

        for item in self.itens:
            self.estoque[item.produto] -= item.quantidade

        endereco = f"{rua}, {numero}, {cidade}/{uf}, CEP {cep}"

        try:
            with open("pedidos.csv", "a", encoding="utf-8") as f:
                f.write(f"{nome};{email};{tipo_cliente};{pagamento};{total};{endereco}\n")
        except OSError as e:
            print("Falha ao salvar pedido: " + str(e))

        mensagem = f"Ola {nome}, seu pedido foi confirmed. "
        if tipo_cliente == "VIP":
            mensagem = f"Ola {nome}, seu pedido foi confirmado. Obrigado por ser VIP! Frete gratis garantido. "
        elif tipo_cliente == "FUNCIONARIO":
            mensagem = f"Ola {nome}, seu pedido foi confirmado. Desconto de colaborador aplicado. "
        mensagem += f"Total: R$ {total:.2f}. Entrega em: {endereco}"
        print(f"[EMAIL para {email}] {mensagem}")

        self.historico.append(f"{nome}|{tipo_cliente}|{total}")
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
        r = "=== RELATORIO DE VENDAS ===\n"
        vip = 0
        comum = 0
        func = 0
        for h in self.historico:
            partes = h.split("|")
            if partes[1] == "VIP":
                vip += 1
            elif partes[1] == "COMUM":
                comum += 1
            elif partes[1] == "FUNCIONARIO":
                func += 1
            r += partes[0] + " (" + partes[1] + "): R$ " + "%.2f" % float(partes[2]) + "\n"
        r += "Pedidos VIP: " + str(vip) + "\n"
        r += "Pedidos COMUM: " + str(comum) + "\n"
        r += "Pedidos FUNCIONARIO: " + str(func) + "\n"
        r += "Total vendido: R$ " + "%.2f" % self.total_vendido + "\n"
        if self.total_vendido > 10000:
            r += "Meta mensal atingida!\n"
        return r

    def verificar_estoque(self):
        alerta = ""
        for produto in self.estoque:
            if self.estoque[produto] < 5:
                alerta += ("ALERTA: " + produto + " com estoque baixo ("
                           + str(self.estoque[produto]) + ")\n")
                print("[EMAIL para compras@loja.com] Repor " + produto)
        return alerta

    def mensagem_promocional(self, tipo_cliente):
        if tipo_cliente == "VIP":
            return "Ofertas exclusivas: 15% em compras acima de R$ 500!"
        elif tipo_cliente == "COMUM":
            return "Compre acima de R$ 500 e ganhe 5% de desconto!"
        elif tipo_cliente == "FUNCIONARIO":
            return "Lembrete: seu desconto de 20% vale em toda a loja."
        else:
            return ""
