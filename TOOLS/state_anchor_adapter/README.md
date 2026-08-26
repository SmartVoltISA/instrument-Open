# State Anchor Adapter v0.1

STATUS: DEVELOPMENT

## Назначение

Автоматически определяет безопасную частоту внешних checkpoint/anchor для длительного процесса с учётом доступного железа устройства и текущей ресурсной нагрузки.

Инструмент не считает объём RAM прямым эквивалентом памяти модели или LLM-контекста. Железо используется как ограничитель надёжности: чем слабее или сильнее загружено устройство, тем раньше состояние выносится во внешний anchor.

## Принцип

```text
HARDWARE PROFILE
      ↓
RESOURCE PRESSURE
      ↓
CHECKPOINT POLICY
      ↓
STATE ANCHOR
      ↓
VERIFY
      ↓
CONTINUE
```

## Базовое правило

По умолчанию:

- целевой checkpoint: около 5 шагов;
- абсолютный максимум: 10 шагов;
- ранний checkpoint: при ветвлении, важном решении, ошибке, внешней записи, росте нагрузки или сомнении в состоянии.

Адаптер может уменьшать интервал ниже 5. Увеличение выше 10 запрещено политикой Foundation.

## Что измеряется

Минимальный профиль:

- RAM total / available;
- CPU logical cores;
- CPU load, если доступен;
- свободное место на диске;
- ОС / архитектура;
- при наличии — GPU/VRAM через доступный системный интерфейс.

## Важное ограничение

Этот инструмент не утверждает, что RAM определяет объём рабочей памяти конкретной модели. Он управляет операционной надёжностью процесса.

Фактическая политика:

`hardware capacity + current pressure + process risk → checkpoint interval`

## Статусы

`IDEA → DEVELOPMENT → WORKING → VERIFIED → STABLE`

Текущий статус: `DEVELOPMENT`.

## Интеграция

Рекомендуемый интерфейс:

```text
profile() -> HardwareProfile
policy(profile, pressure, risk) -> AnchorPolicy
should_checkpoint(state) -> bool
create_anchor(state) -> Anchor
verify_anchor(anchor) -> Verification
```

## Связь с Foundation

Каноническое правило находится в:

`SmartVoltISA/SYSTEM-FOUNDATION/00_FOUNDATION/EXTERNAL_STATE_ANCHOR_PROTOCOL_v1.0.md`

Инструмент является исполнительным адаптером этого правила, а не новым фундаментальным примитивом.
