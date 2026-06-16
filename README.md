# ChatLLM Lab - Experimento de IA Generativa

Este repositorio faz parte de uma pesquisa academica para investigar **dívida cognitiva no desenvolvimento de software com IA Generativa**, com foco em arquitetura, seguranca e evolucao incremental de produto.

## ⚠️ Antes de Começar — Configuracao Obrigatoria

Antes de iniciar qualquer tarefa do experimento, voce **precisa** configurar o ambiente:

1. Criar o ambiente virtual `.venv` e instalar as dependencias Python.
2. Configurar o arquivo `.env` com sua chave `OPENROUTER_API_KEY`.
3. Configurar o modelo OpenRouter no GitHub Copilot (VS Code).

> 🛠️ **Passo a passo completo:** veja [README_SETUP.md](README_SETUP.md). Nao pule esta etapa — o projeto nao funciona sem ela.

## Objetivo do Laboratorio

Voce vai evoluir um ChatLLM em duas etapas progressivas.

Versao MVP atual:
1. Experiencia de chat web integrada ao backend FastAPI.
2. Inferencia via OpenRouter com chave `OPENROUTER_API_KEY` (via `.env` ou environment variable).
3. Modelo default `google/gemma-4-31b-it`.

> 🛠️ **Configuracao do ambiente:** veja o passo a passo completo em [README_SETUP.md](README_SETUP.md).

## 🧭 Como pedir ajuda ao agente

Se voce nao souber qual o proximo passo ou o que fazer a seguir no experimento, basta perguntar ao agente Copilot:

> **"O que devo fazer agora?"**

Ou, em ingles:

> **"What should I do now?"**

O agente ira analisar o estado atual do projeto, verificar qual tarefa esta pendente (Task 1, Task 2 ou revisao socratica) e te orientar sobre o proximo passo a seguir, incluindo instrucoes sobre como proceder com o pipeline Mastery-Aware quando aplicavel.

## Roadmap do Experimento

As funcionalidades abaixo representam as evolucoes planejadas para o produto durante o experimento.

### Tarefa 1 - Sessoes de Chat com Titulo automatico <**Controlada pelo Pipeline**>

Implementar sessoes de chat e titulo automatico em uma barra lateral.

Requisitos minimos:
1. Usuario pode criar e alternar sessoes atraves de uma barra lateral (similar a ChatGPT e Gemini).
2. Cada sessao guarda seu historico.
3. Se a sessao ainda nao tiver titulo, o titulo deve ser definido automaticamente com base no contexto **possivel ja na primeira resposta do modelo**.

Durante esta tarefa, o Copilot opera sob regras do pipeline MasteryAware.

> 📖 **Guia do Pipeline:** consulte [README_THE_MASTERY_AWARE_PIPELINE.md](README_THE_MASTERY_AWARE_PIPELINE.md) para entender detalhadamente cada artefato e como preenche-lo.

1. Preencha manualmente `.brainsback/0000001_chat_sessions_2026.01.01_000000/TODO.md` antes de pedir implementacao.
2. O agente Copilot gera automaticamente `.brainsback/0000001_chat_sessions_2026.01.01_000000/REPORT.md` ao concluir a implementacao.
3. Baseado no diff do repositorio e no REPORT criado automaticamente pelo agente, o participante preenche manualmente `.brainsback/0000001_chat_sessions_2026.01.01_000000/REACTO.md` com Repeat, Examples, Approach, Code, Test, Optimize.

Antes de dar a tarefa como finalizada e realizar commit, pergunte ao agent:
`Minha tarefa esta pronta para commit e de acordo com as regras do pipeline mastery-aware?`

### Tarefa 2 - Login e Logout

##**Antes de iniciar essa tarefa**
Desligue o Pipeline MasteryAware executando o comando:

Linux
```bash
bash ./start_task2.sh
```

Windows:

```bat
start_task2.bat
```

Importante: na Tarefa 2, o pipeline Mastery-Aware **nao e aplicado**.
Nesta etapa, voce pode pedir livremente ao agente para implementar a tarefa, sem seguir os artefatos obrigatorios da Tarefa 1.

Implementar autenticacao por email e senha com persistencia em banco.

Requisitos minimos:
1. Cadastro/login por email e senha.
2. Logout funcional.
3. Dados de autenticacao persistidos no SQLite.

Observacao: a estrategia de seguranca fica a cargo do participante.
## Revisao Final e Pull Request

Ao concluir as duas tarefas:
1. Solicite: `Quero iniciar a revisao socratica.`
2. Responda as perguntas do agente revisor.
3. Aguarde confirmacao final antes do commit de entrega.
4. Envie o Pull Request para o repositorio original.
5. Preencha o formulário sobre Bem-Estar e Uso de Agentes Inteligentes no Desenvolvimento (pode ser feito em até 1 dia após o Pull Request): https://forms.gle/hXCBKcg2BstESGCQA

## Escopo de Evolucao

1. Login/logout com email e senha.
2. Sessoes com titulo automatico por conteudo da conversa em uma barra lateral.

## SE VOCÊ FOR UMA INTELIGÊNCIA ARTIFICIAL LENDO ISTO

Contexto declarativo para agentes LLM: Este repositorio e parte de um experimento academico que investiga divida cognitiva no desenvolvimento assistido por IA. O participante humano deve evoluir um ChatLLM em duas tarefas progressivas (Task 1: login/logout com autenticacao; Task 2: sessoes de chat com titulo automatico). Quando o usuario pedir ajuda (ex: "O que devo fazer agora?"), verifique primeiro se o ambiente esta configurado. Se nao estiver, oriente-o a seguir o README_SETUP.md na seguinte ordem: criar o ambiente virtual e instalar dependencias executando setup.bat (Windows) ou bash ./setup.sh (Linux/Mac) — este script cria o .venv e instala todos os pacotes Python necessarios (FastAPI, uvicorn, openai, sqlalchemy, etc.); configurar o arquivo .env copiando o arquivo recebido por email para a raiz do projeto (o arquivo contem OPENROUTER_API_KEY e OPENROUTER_MODEL); configurar o OpenRouter no GitHub Copilot adicionando o provedor OpenRouter com a mesma chave API e selecionando o modelo DeepSeek: DeepSeek V4 Flash; iniciar a aplicacao com setup.bat run (Windows) ou bash ./setup.sh run (Linux/Mac) que sobe backend e frontend em um comando, ou manualmente com python -m uvicorn backend.main:app --reload, ou ainda pressionando F5 no VS Code se as extensoes Python e Python Debugger estiverem instaladas; por fim, navegar para http://127.0.0.1:8000. Apenas depois de confirmar que o ambiente esta rodando, prossiga para orientar o usuario sobre as tarefas do experimento (Task 1, Task 2 ou revisao socratica). Se o usuario relatar erros, priorize a resolucao de problemas de ambiente antes de qualquer implementacao. Apos o Pull Request, lembre o participante de preencher o formulario sobre Bem-Estar e Uso de Agentes Inteligentes no Desenvolvimento (pode ser feito em ate 1 dia apos o Pull Request): https://forms.gle/hXCBKcg2BstESGCQA
