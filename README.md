# CirquloFit API

API backend para o sistema de gamificação de treinos CirquloFit, desenvolvida com FastAPI e PostgreSQL.

## 🚀 Características

- **FastAPI** - Framework moderno e rápido para APIs Python
- **PostgreSQL** - Banco de dados robusto para produção
- **Autenticação JWT** - Sistema seguro de autenticação
- **Gamificação** - Sistema de XP, níveis e conquistas
- **Tracking de Treinos** - Acompanhamento completo de sessões
- **Docker** - Containerização para deploy

## 🏗️ Arquitetura

```
app/
├── core/           # Configurações e constantes
├── domain/         # Entidades e regras de negócio
├── application/    # Serviços e casos de uso
├── infrastructure/ # Conexão com banco de dados
└── routers/       # Endpoints da API
```

## 📋 Funcionalidades

### Autenticação
- Registro de usuários
- Login com JWT
- Validação de tokens
- Perfis de usuário

### Treinos
- Criação de treinos personalizados
- Treinos pré-definidos por nível
- Sistema de evolução progressiva
- Categorização por objetivos

### Sessões
- Início de sessões de treino
- Tracking de exercícios
- Cálculo de XP e progresso
- Finalização com estatísticas

### Gamificação
- Sistema de XP por ações
- Níveis progressivos
- Streaks e conquistas
- Estatísticas detalhadas

### Dashboard
- Progresso semanal
- Calendário de treinos
- Evolução de cargas
- Métricas de performance

## 🛠️ Tecnologias

- **FastAPI** 0.118.0
- **PostgreSQL** com psycopg2
- **Python 3.11+**
- **JWT** para autenticação
- **bcrypt** para hash de senhas
- **Docker** para containerização

## 🚀 Instalação e Execução

### Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Executar aplicação
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build da imagem
docker build -t cirqulofit-api .

# Executar container
docker run -p 8000:8000 cirqulofit-api
```

## 📚 Endpoints da API

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Dados do usuário atual

### Treinos
- `GET /api/workouts` - Listar treinos do usuário
- `POST /api/workouts` - Criar novo treino
- `GET /api/workouts/{id}` - Detalhes do treino
- `POST /api/workouts/{id}/start` - Iniciar sessão
- `POST /api/workouts/sessions/{id}/complete` - Finalizar sessão

### Dashboard
- `GET /api/workouts/dashboard` - Dados do dashboard
- `GET /api/workouts/stats` - Estatísticas do usuário

### GIFs
- `GET /api/gifs/{exercise}` - GIF de demonstração do exercício

## 🔧 Configuração

### Variáveis de Ambiente

```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://user:password@localhost/cirqulofit
```

### Banco de Dados

A aplicação cria automaticamente as tabelas necessárias:
- `users` - Usuários
- `workouts` - Treinos
- `workout_sessions` - Sessões de treino
- `workout_exercises` - Exercícios das sessões
- `user_progress` - Progresso dos usuários

## 📊 Estrutura do Banco

### Tabela `users`
- `id` - ID único
- `name` - Nome do usuário
- `email` - Email único
- `hashed_password` - Senha criptografada
- `gender` - Gênero
- `is_active` - Status ativo
- `created_at` - Data de criação

### Tabela `workouts`
- `id` - ID único
- `user_id` - ID do usuário
- `name` - Nome do treino
- `description` - Descrição
- `category` - Categoria
- `level` - Nível de dificuldade
- `duration` - Duração estimada
- `exercises_count` - Número de exercícios
- `xp_reward` - XP de recompensa

### Tabela `workout_sessions`
- `id` - ID único
- `user_id` - ID do usuário
- `workout_id` - ID do treino
- `started_at` - Início da sessão
- `completed_at` - Fim da sessão
- `duration` - Duração em minutos
- `xp_earned` - XP ganho
- `is_completed` - Status de conclusão

## 🎯 Sistema de Gamificação

### XP por Ações
- **Iniciar sessão:** 10 XP
- **Treinar (por exercício):** 5 XP
- **Completar sessão:** 20 XP
- **Streak diário:** 5 XP bônus

### Níveis
- **Ameba** (1-10): Sedentário iniciante
- **Bactéria** (11-25): Primeiros passos
- **Protozoário** (26-50): Ganhando forma
- **Inseto** (51-100): Evoluindo
- **Peixe** (101-200): Nadando bem
- **Réptil** (201-350): Sangue frio
- **Ave** (351-500): Voando alto
- **Mamífero** (501-750): Sangue quente
- **Primata** (751-1000): Quase humano
- **Humano** (1000+): Evolução completa

## 🐳 Docker

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
api:
  build: ./cirqulo-fit-api
  ports:
    - "8000:8000"
  environment:
    - DATABASE_URL=postgresql://cirqulofit_user:cirqulofit_password@db:5432/cirqulofit
  depends_on:
    - db
```

## 📈 Monitoramento

### Health Check
- `GET /health` - Status da aplicação
- `GET /` - Informações da API

### Logs
- Logs estruturados para debugging
- Tratamento de erros centralizado
- Métricas de performance

## 🔒 Segurança

- **JWT** para autenticação
- **bcrypt** para hash de senhas
- **CORS** configurado
- **Validação** de dados de entrada
- **Sanitização** de queries SQL

## 🧪 Testes

```bash
# Executar testes
pytest

# Testes com coverage
pytest --cov=app
```

## 📝 Documentação

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI:** `http://localhost:8000/openapi.json`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Desenvolvimento:** Equipe CirquloFit
- **Arquitetura:** Clean Architecture
- **Deploy:** Docker + PostgreSQL

---

**CirquloFit API** - Transformando treinos em jogos! 🎮💪
