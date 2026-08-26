# Adaptive State Anchor Adapter v0.2

**Status: Experimental / portable**

Инструмент автоматически выбирает безопасную частоту внешнего checkpoint для длительного процесса.

```text
USER_DATA_INPUT
      ↓
HARDWARE PROFILE + CONTINUITY RISK
      ↓
ADAPTIVE POLICY
      ↓
DURABLE STATE ANCHOR
      ↓
VERIFY
      ↓
RECOVERY / CONTINUE
```

## Что адаптируется

- доступная RAM и её давление;
- CPU и текущая нагрузка;
- свободное место на диске;
- GPU/VRAM, если доступно, как часть профиля;
- риск процесса: `low / normal / high / critical`;
- число шагов после последнего checkpoint;
- критические события;
- наблюдаемая continuity risk: unresolved/unknown, contradictions/errors, branching/decisions, state completeness/growth, verification age и recent state change.

Базовый интервал — 5 шагов. Абсолютный максимум — 10. Рост риска или нагрузки только уменьшает интервал.

## Continuity Risk Detector

Выдаёт:

`NORMAL → WATCH → ELEVATED → CRITICAL`

плюс рекомендуемый checkpoint target и флаг немедленного checkpoint. Работает только с явно переданными метриками процесса; не измеряет скрытый контекст или память модели.

Статус: `EXPERIMENTAL`; пороги требуют калибровки.

## Установка

Зависимости: Python 3.10+; `psutil` необязателен.

## Использование

```bash
python state_anchor_adapter.py profile
python state_anchor_adapter.py policy --risk normal --steps 3
python state_anchor_adapter.py checkpoint --state '{"objective":"demo","status":"WORKING"}'
python state_anchor_adapter.py verify .anchors/<anchor>.json
python continuity_risk_detector.py --state '{"unresolved":["x"],"unknown":["y"]}' --steps 4
```

## Проверка

В репозитории есть тесты detector и GitHub Actions workflow для syntax/test checks. До фактического CI run статус остаётся `Experimental`.

## Anchor

Каждый anchor содержит схему, идентификатор, время, профиль ресурсов, применённую политику, событие, состояние и SHA-256 digest. Запись выполняется атомарной заменой временного файла.

Пользовательские данные передаются только через входной `state`; инструмент не содержит данных конкретного проекта.

## Ограничения

Пороговые значения — инженерные эвристики. Их необходимо проверять на конкретном наборе устройств и рабочих процессов перед переводом инструмента в стабильный статус.

Аппаратные параметры не являются оценкой объёма контекста или памяти конкретной модели. Они используются только для управления операционной надёжностью.

## Лицензия

См. `LICENSE` репозитория.
