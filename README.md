# Qualitech CRM Contencioso (MVP)

Sistema web desenvolvido em arquitetura monolítica em camadas (MVC) para centralizar a gestão, triagem de prazos (SLA) e rastreabilidade documental de demandas regulatórias e de pré-defesa da Qualitech (Bacen, Consumidor.gov.br, Procon e Reclame Aqui).

## Pilha Tecnológica
* **Linguagem:** Python 3.12
* **Framework Web:** Flask 3.0.x (com Flask-Login)
* **ORM e Banco de Dados:** SQLAlchemy 2.0.x e PostgreSQL 16
* **Interface:** HTML5, CSS3, JavaScript e Bootstrap 5.3.x (acessibilidade WCAG 2.1 AA)

## Funcionalidades Principais do MVP
* **RF01:** Autenticação segura e controle de acesso por perfil (Analista e Gestor).
* **RF02:** Cadastro unificado de demandas com bloqueio automático de protocolos duplicados.
* **RF03:** Fila única de atendimentos ordenada por vencimento de SLA com indicadores multimodais.
* **RF04:** Linha do tempo imutável de tratativas, anexo comprobatório e encerramento com parecer final.
