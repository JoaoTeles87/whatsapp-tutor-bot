# Requirements Document

## Introduction

O Agente Educacional Nino é um chatbot para WhatsApp que atua como tutor virtual para alunos do 6º ano. O sistema se conecta à Evolution API existente para receber e enviar mensagens, processando perguntas dos alunos com respostas empáticas e informativas baseadas em contexto educacional.

## Glossary

- **Nino**: O nome do agente conversacional que interage com os alunos
- **Agent System**: Sistema principal que processa mensagens e gera respostas usando LLM
- **Evolution API**: API de integração com WhatsApp já configurada que envia e recebe mensagens
- **Webhook Handler**: Componente que recebe notificações HTTP de mensagens do WhatsApp
- **Message History**: Armazenamento em memória do histórico de conversas por aluno
- **LLM Provider**: Serviço de linguagem (OpenAI ou similar) usado para gerar respostas

## Requirements

### Requirement 1

**User Story:** Como desenvolvedor, eu quero receber mensagens do WhatsApp via webhook da Evolution API, para que o sistema possa processar mensagens dos alunos em tempo real

#### Acceptance Criteria

1. THE Webhook Handler SHALL expor um endpoint HTTP POST em /webhook para receber notificações da Evolution API
2. WHEN uma mensagem é recebida no webhook, THE Webhook Handler SHALL extrair o número do remetente e o conteúdo da mensagem do payload
3. WHEN uma mensagem é recebida, THE Webhook Handler SHALL validar que o payload contém os campos obrigatórios antes do processamento
4. THE Webhook Handler SHALL retornar status HTTP 200 para confirmar recebimento da mensagem

### Requirement 2

**User Story:** Como desenvolvedor, eu quero enviar respostas para o WhatsApp via Evolution API, para que os alunos recebam as mensagens do Nino

#### Acceptance Criteria

1. WHEN o Agent System gera uma resposta, THE Agent System SHALL enviar a mensagem via Evolution API usando requisição HTTP POST
2. THE Agent System SHALL incluir o número do destinatário e o texto da mensagem no corpo da requisição
3. IF o envio de mensagem falha, THEN THE Agent System SHALL registrar o erro em log
4. THE Agent System SHALL usar as credenciais e URL da Evolution API configuradas em variáveis de ambiente

### Requirement 3

**User Story:** Como desenvolvedor, eu quero manter histórico de conversas em memória, para que o agente tenha contexto das interações anteriores com cada aluno

#### Acceptance Criteria

1. THE Message History SHALL armazenar mensagens indexadas por número de telefone do remetente
2. WHEN uma nova mensagem é adicionada, THE Message History SHALL incluir o papel (user ou assistant) e o conteúdo da mensagem
3. THE Message History SHALL fornecer o histórico completo de um remetente quando solicitado pelo Agent System
4. THE Message History SHALL limitar o histórico a 20 mensagens por remetente para controlar uso de memória

### Requirement 4

**User Story:** Como aluno, eu quero conversar com o Nino e receber respostas empáticas e úteis, para que eu me sinta acolhido e apoiado

#### Acceptance Criteria

1. WHEN o Agent System recebe uma mensagem de aluno, THE Agent System SHALL usar o LLM Provider para gerar uma resposta
2. THE Agent System SHALL incluir o histórico de conversa como contexto para o LLM Provider
3. THE Agent System SHALL usar um system prompt que define Nino como colega de classe empático do 6º ano
4. THE Agent System SHALL gerar respostas usando linguagem apropriada para alunos do 6º ano com emojis quando apropriado

### Requirement 5

**User Story:** Como desenvolvedor, eu quero configurar o sistema via variáveis de ambiente, para que o sistema possa ser facilmente implantado em diferentes ambientes

#### Acceptance Criteria

1. THE Agent System SHALL carregar configurações de um arquivo .env na inicialização
2. THE Agent System SHALL requerer as seguintes variáveis: EVOLUTION_API_URL, EVOLUTION_API_KEY, LLM_API_KEY
3. THE Agent System SHALL usar valores padrão para configurações opcionais como porta do servidor
4. IF variáveis obrigatórias estão ausentes, THEN THE Agent System SHALL registrar erro e não inicializar

### Requirement 6

**User Story:** Como desenvolvedor, eu quero executar o sistema em um ambiente virtual Python, para que as dependências sejam isoladas e gerenciadas corretamente

#### Acceptance Criteria

1. THE Agent System SHALL fornecer um arquivo requirements.txt com todas as dependências necessárias
2. THE requirements.txt SHALL listar pacotes sem versões fixas para permitir flexibilidade
3. THE Agent System SHALL incluir documentação para criar e ativar um ambiente virtual Python
4. THE Agent System SHALL ser executável via comando python após instalação das dependências
