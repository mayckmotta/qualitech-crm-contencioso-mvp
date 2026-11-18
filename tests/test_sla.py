import unittest
from datetime import datetime, timedelta
from app import app, db, arquivo_permitido
from models import Usuario, Demanda, Tratativa

class TesteIntegracaoCRM(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        usuario = Usuario(nome='Analista Teste', email='teste@qualitech.com', perfil='Analista')
        usuario.definir_senha('SenhaForte123')
        db.session.add(usuario)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(usuario.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_calculo_sla_unitario(self):
        vencida = Demanda(
            protocolo='BCB-001', canal='Bacen', reclamante='Ana',
            cpf='111.111.111-11', data_limite=datetime.now() - timedelta(hours=1), resumo='Teste'
        )
        no_prazo = Demanda(
            protocolo='PRC-002', canal='Procon', reclamante='Bruno',
            cpf='222.222.222-22', data_limite=datetime.now() + timedelta(days=2), resumo='Teste'
        )
        self.assertEqual(vencida.calcular_sla(), 'Vencido')
        self.assertEqual(no_prazo.calcular_sla(), 'No prazo')

    def test_validacao_extensao_anexo(self):
        self.assertTrue(arquivo_permitido('comprovante.pdf'))
        self.assertFalse(arquivo_permitido('script_malicioso.exe'))

    def test_cadastro_e_bloqueio_duplicidade_integracao(self):
        dados = {
            'protocolo': 'BCB-2026-999',
            'canal': 'Bacen',
            'reclamante': 'Carlos Silva',
            'cpf': '333.333.333-33',
            'data_limite': '2026-12-20T15:00',
            'resumo': 'Contestacao de tarifa'
        }
        resp1 = self.client.post('/demanda/nova', data=dados, follow_redirects=True)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(Demanda.query.count(), 1)

        resp2 = self.client.post('/demanda/nova', data=dados, follow_redirects=True)
        self.assertEqual(Demanda.query.count(), 1)

    def test_tratativa_e_encerramento_integracao(self):
        demanda = Demanda(
            protocolo='PRO-2026-555', canal='Procon', reclamante='Maria Souza',
            cpf='444.444.444-44', data_limite=datetime.now() + timedelta(days=1), resumo='Estorno'
        )
        db.session.add(demanda)
        db.session.commit()

        resp = self.client.post(f'/demanda/{demanda.id}/tratar', data={
            'status': 'Concluído',
            'descricao': 'Estorno efetuado e comprovado no portal.'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Demanda.query.get(demanda.id).status, 'Concluído')
        self.assertEqual(Tratativa.query.count(), 1)

if __name__ == '__main__':
    unittest.main()
    
