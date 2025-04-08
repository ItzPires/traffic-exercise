# Descrição
Esta API REST foi desenvolvida com Django e Django Rest Framework para monitorizar a intensidade de tráfego rodoviário em segmentos de estrada. A API permite gerir segmentos de estrada, leituras de velocidade média, sensores de tráfego e veículos.

## Funcionalidades Principais
- Gestão de Segmentos de Estrada: CRUD completo para administradores, com leitura apenas para utilizadores anónimos.

- Leituras de Velocidade: Registo de velocidades médias com cálculo automático da intensidade de tráfego (elevada, média, baixa).

- Sensores de Tráfego: Registo de passagens de veículos com autenticação por API Key.

- Filtros: Filtragem de segmentos por intensidade de tráfego e histórico de veículos nas últimas 24 horas.

## Instalação e Configuração
### Pré-requisitos
- Docker
- Docker Compose

### Configuração
* Clone o Repositório
~~~
git clone https://github.com/ItzPires/traffic-exercise.git
cd traffic-exercise
~~~

* Crie e inicie os containers:

~~~
cd docker/dev
docker compose up --build
~~~

* A API estará disponível em http://localhost:8000

#### Variáveis de Ambiente
Variáveis no ficheiro .env

## Utilização
#### Segmentos de Estrada (/roadsegment/)
- GET: Lista todos os segmentos (ou por intensidade com /roadsegment/?intensity={high, medium, low})
- POST: Cria um novo segmento (apenas administradores)
- PUT/PATCH: Atualiza um segmento (apenas administradores)
- DELETE: Remove um segmento (apenas administradores)

#### Leituras de Velocidade (/speedreading/)
- GET: Lista todas as leituras
- POST: Regista uma nova leitura (apenas administradores)

#### Veículos (/cars/)
- GET /last_24h_observations/?license_plate=AABBCC: Lista observações de um veículo nas últimas 24 horas

#### Sensores (/sensors/)
- POST /trafficobservations/: Regista observações de sensores (requer API Key)

#### Administração
Django Admin em http://localhost:8000/admin/

## Testes
Para executar os testes basta iniciar o docker de testes que automaticamente serão realizados:
~~~
cd docker/test
docker compose up --build
~~~

## Documentação
Documentação em http://localhost:8000/api/docs/

