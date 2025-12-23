# MerchantAgent

## Назначение
Оценивает риск, связанный с продавцом (merchant), независимо от клиента. Агент полностью rule-based и не вызывает LLM.

## Контракт входных данных
Агент читает следующие поля из `Transaction`:
- `merchant`
- `merchant_category`
- `merchant_type`
- `merchant_risk_score`
- `high_risk_merchant`
- `amount`
- `card_present`
- `channel`

## Основные правила (сигналы)
1) Риск-скор мерчанта  
Если задан `merchant_risk_score`, он добавляется к score и формирует причину уровня HIGH/MEDIUM по порогам.

2) Флаг high-risk merchant  
Если `high_risk_merchant=true`, добавляется фиксированный буст и причина.

3) Высокорисковая категория  
Нормализуется `merchant_category`, затем проверяется на принадлежность `HIGH_RISK_CATEGORIES`.

4) Онлайн + высокая сумма  
Определяется online/offline по `channel` → `merchant_type` → `card_present`.  
Если статус online не определен (None), правило не срабатывает.  
Если online и `amount` превышает порог (общий или по категории), добавляется буст и причина.

5) Подозрительное имя  
Список стоп‑слов + базовые эвристики (цифровые/пустые/служебные значения).

## Конфигурация
Все пороги, списки и бусты лежат в `src/anti_fraud/agents/merchant/config.py`:
- `HIGH_RISK_CATEGORIES`
- `CATEGORY_SYNONYMS`
- `CATEGORY_AMOUNT_THRESHOLDS`
- `SUSPICIOUS_MERCHANT_NAMES`
- `HIGH_AMOUNT_THRESHOLD`
- `RISK_SCORE_HIGH`, `RISK_SCORE_MEDIUM`
- `BOOST_*`
- `ONLINE_CHANNELS`, `OFFLINE_CHANNELS`

Примечание: `CATEGORY_AMOUNT_THRESHOLDS` сейчас рассчитаны по P95 `amount` на каждую категорию из `synthetic_fraud_data.csv`
и рассчитаны для категорий в формате, встречающемся в датасете (например, `grocery`, `restaurant`). Это эвристика под
текущие данные, а не универсальные пороги.

## Архитектура правил
Каждое правило — отдельный класс в `src/anti_fraud/agents/merchant/rules.py`, единый контракт:
- вход: `Transaction` + `MerchantRuleContext`
- выход: `RuleResult(score_delta, reasons, features)`

Набор правил конфигурируется через DI:
```python
from anti_fraud.agents.merchant.agent import MerchantAgent
from anti_fraud.agents.merchant.rules import HighRiskCategoryRule, SuspiciousNameRule

agent = MerchantAgent(rules=[HighRiskCategoryRule(), SuspiciousNameRule()])
```

## Выход
Возвращает `AgentResult` со значениями:
- `score` (0..1, с cap=1.0; если сумма сигналов выше, применяется ограничение)
- `risk_level` (LOW/MEDIUM/HIGH)
- `explanation` (строка причин)
- `features_used` (список фич)
- `reasons` (список причин)

## Ограничения
- Пороги/веса не калиброваны под валюту/регион.
- Нет исторических метрик мерчанта (fraud rate/chargebacks/velocity).
- Причины — свободный текст без reason‑codes.

## Будущие фичи
- Калибровка порогов/весов под данные и версии политик скоринга.
- Валютная нормализация сумм (конвертация в базовую валюту).
- Исторические агрегаты по мерчанту (fraud rate, chargeback rate, merchant velocity).
- Reason codes + локализация причин для BI и explainability.
- Политика агрегации конфликтующих сигналов (soft-cap, max, normalized blend).
- Тесты на правила и контекст (юнит‑набор для регрессий).
