# План подготовки Docker-инфраструктуры

Документ описывает этапы и артефакты для контейнеризации мультиагентной системы
и ее будущего Kafka-ориентированного окружения.

## 1) Определить состав сервисов
- Orchestrator (consumer `transactions`, producer `agent.*.requests`)
- Набор агентов (Velocity, Profile, Geo, Device, Merchant, ML)
- DecisionAgent (consumer `agent.*.results`, producer `decision.results`)
- Kafka (broker + zookeeper/ kraft)
- (опционально) Schema-less валидация/adapter сервис
- (опционально) хранилище: ClickHouse/Timescale/Redis

## 2) Структура Docker-артефактов
- `docker/`
  - `orchestrator/` (Dockerfile)
  - `agents/velocity/` ... (Dockerfile)
  - `agents/profile/` ...
  - `decision/` (Dockerfile)
- `docker-compose.yml` (локальная разработка)
- `docker-compose.kafka.yml` (Kafka-only или расширенный профиль)
- `.env` (переменные окружения)

## 3) Базовые Dockerfile (Python)
- Общий базовый образ (опционально): `python:3.11-slim`
- Установка зависимостей из `pyproject.toml`
- Команда запуска через `python -m ...`
- Healthcheck (минимальный endpoint или проверка процесса)

## 4) docker-compose для локального запуска
Минимально:
- Kafka (single broker)
- Orchestrator
- 1–2 агента для MVP
- DecisionAgent

Профили:
- `mvp` (минимум сервисов)
- `full` (все агенты + хранилища)

## 5) Конфигурация и переменные окружения
- `KAFKA_BOOTSTRAP_SERVERS`
- `KAFKA_CONSUMER_GROUP`
- `KAFKA_TOPIC_TRANSACTIONS`
- `KAFKA_TOPIC_AGENT_REQUESTS_PREFIX`
- `KAFKA_TOPIC_AGENT_RESULTS_PREFIX`
- `KAFKA_TOPIC_DECISION_RESULTS`
- `SCHEMA_VERSION_DEFAULT`

## 6) Локальные скрипты
- `scripts/dev-up.sh` (compose up)
- `scripts/dev-down.sh` (compose down)
- `scripts/seed-kafka.sh` (тестовые сообщения)

## 7) Базовые тесты инфраструктуры
- Проверка доступности Kafka
- Прогон тестового `transactions` сообщения
- Проверка попадания результата в `decision.results`

## 8) Этапность внедрения
1) Dockerize текущий код (MerchantAgent + Orchestrator/Decision skeleton)
2) Добавить Kafka и минимальные топики
3) Поднять остальные агенты
4) Подключить хранилища (time-series/state)

## 9) Принципы
- Один сервис = один контейнер
- Логи в stdout
- Без schema registry на старте
- Все конфиги через env vars

## 10) Следующие шаги
- Уточнить список сервисов MVP
- Определить команды запуска для каждого агента
- Подготовить `docker-compose.yml` и Dockerfile для MVP
