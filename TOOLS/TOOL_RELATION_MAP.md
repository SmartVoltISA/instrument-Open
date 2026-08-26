# Карта связей инструментов

| Узел | Роль | Вход | Выход | Следующий узел |
|---|---|---|---|---|
| Editor | создание/изменение | данные | изменённое состояние | Terminal / Git |
| Terminal | выполнение | команда/состояние | фактический результат | Verify |
| Verify | проверка | результат | pass/fail + evidence | Feedback / Git |
| Git | история состояния | изменения | commit/diff | GitHub |
| GitHub | удалённое состояние | commit | опубликованное состояние | потребитель |
| Guardian | контроль границы | portable candidate | pass/fail | Public layer |
| Graph Memory Inspector | структурная проверка графа | graph | findings | потребитель / feedback |
| State Anchor Adapter | адаптивное сохранение состояния | hardware + load + process risk + state | checkpoint policy + durable anchor | Verify / Recovery / Git |

## Правило

Связь между узлами должна быть объяснима через вход, выход и проверяемое состояние.

Если результат одного узла нельзя однозначно передать следующему узлу, связь считается неполной.

## State Anchor Adapter

```text
Hardware Profile
      ↓
Resource Pressure
      ↓
Process Risk
      ↓
Checkpoint Policy
      ↓
External Anchor
      ↓
Verify
      ↓
Continue / Recover
```

Железо не считается эквивалентом памяти модели. Оно используется как инженерный фактор надёжности и ресурсного риска.

Базовое ограничение Foundation: целевой интервал около 5 шагов, максимум 10; адаптер имеет право уменьшать интервал при слабом железе, высокой нагрузке или высоком риске.

## Граница публикации

`Private source → Guardian → Portable tool → Public repository`

Guardian является обязательным контрольным узлом перед публичной публикацией переносимого инструмента.
