import unittest
import os
from gerenciador_pedidos import GerenciadorPedidos

class TestGerenciadorPedidosCaracterizacao(unittest.TestCase):

    def setUp(self):
        self.gerenciador = GerenciadorPedidos()

    def tearDown(self):
        if os.path.exists("pedidos.csv"):
            os.remove("pedidos.csv")

    def test_validacao_nome_invalido(self):
        res = self.gerenciador.processar_pedido("", "teste@email.com", "COMUM", "PIX", 1, "Rua A", "10", "Recife", "PE", "50000-000")
        self.assertEqual(res, "ERRO: cliente sem nome")

    def test_validacao_email_invalido(self):
        res = self.gerenciador.processar_pedido("João", "email_invalido", "COMUM", "PIX", 1, "Rua A", "10", "Recife", "PE", "50000-000")
        self.assertEqual(res, "ERRO: email invalido")

    def test_validacao_pedido_vazio(self):
        res = self.gerenciador.processar_pedido("João", "joao@email.com", "COMUM", "PIX", 1, "Rua A", "10", "Recife", "PE", "50000-000")
        self.assertEqual(res, "ERRO: pedido vazio")

    def test_processar_pedido_sucesso_pix_desconto_e_frete(self):
        self.gerenciador.adicionar_item("CANETA", 10, 10.0) # Subtotal: 100.0
        # Cliente COMUM (< 500 sem desconto), Frete PE = 12.50. Total intermediário = 112.50
        # Pagamento PIX (5% desc) = 112.50 * 0.95 = 106.875 -> round = 106.88
        res = self.gerenciador.processar_pedido(
            "Maria", "maria@email.com", "COMUM", "PIX", 1,
            "Rua B", "123", "Recife", "PE", "50000-000"
        )
        self.assertEqual(res, "OK: 106.88")
        self.assertEqual(self.gerenciador.estoque["CANETA"], 90)

    def test_cliente_vip_frete_gratis(self):
        self.gerenciador.adicionar_item("CADERNO", 1, 100.0)
        # VIP recebe 10% desc (< 500) -> 90.0. Frete é 0 para VIP.
        # Pagamento PIX (5% desc) -> 90.0 * 0.95 = 85.50
        res = self.gerenciador.processar_pedido(
            "Carlos", "carlos@email.com", "VIP", "PIX", 1,
            "Rua C", "45", "Natal", "RN", "59000-000"
        )
        self.assertEqual(res, "OK: 85.50")

    def test_calcular_orcamento_igual_ao_calculo_pedido(self):
        self.gerenciador.adicionar_item("MOCHILA", 2, 200.0) # Subtotal: 400.0
        # FUNCIONARIO (20% desc) -> 320.0 (subtotal - desc = 320 > 300 -> Frete Grátis)
        orcamento = self.gerenciador.calcular_orcamento("FUNCIONARIO", "BA")
        self.assertEqual(orcamento, 320.0)

    def test_verificar_estoque_alerta(self):
        self.gerenciador.estoque["CALCULADORA"] = 2
        alerta = self.gerenciador.verificar_estoque()
        self.assertIn("ALERTA: CALCULADORA com estoque baixo (2)", alerta)

if __name__ == "__main__":
    unittest.main()