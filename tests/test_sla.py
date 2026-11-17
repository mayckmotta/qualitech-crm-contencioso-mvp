import unittest
from datetime import datetime, timedelta
from models import Demanda

class TesteCalculoSLA(unittest.TestCase):
    def test_demanda_vencida(self):
        demanda = Demanda(
            protocolo='BCB-2026-001',
            canal='Bacen',
            reclamante='Teste',
            cpf='000.000.000-00',
            data_limite=datetime.now() - timedelta(hours=2),
            resumo='Teste vencido'
        )
        self.assertEqual(demanda.calcular_sla(), 'Vencido')

    def test_demanda_no_prazo(self):
        demanda = Demanda(
            protocolo='PRC-2026-002',
            canal='Procon',
            reclamante='Teste',
            cpf='000.000.000-00',
            data_limite=datetime.now() + timedelta(days=3),
            resumo='Teste no prazo'
        )
        self.assertEqual(demanda.calcular_sla(), 'No prazo')

if __name__ == '__main__':
    unittest.main()
