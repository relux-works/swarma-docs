# Рисунки книги об a2a: манифест

Рисунки книги об a2a рисует тот же генератор `scripts/diagram-kit/render.py` по тем же правилам `editorial/diagram-style.ru.md`, что и рисунки книги Swarma. Исходник TOML лежит в этом каталоге, рендер ложится в `a2a-book/diagrams/<имя>.svg`:

```
mkdir -p a2a-book/diagrams
python3 scripts/diagram-kit/render.py a2a-book/src/<имя>.toml a2a-book/diagrams/<имя>.svg --report --require-fit <поле>
```

Поле `tall` (167 × 168 мм) получает рисунок, чья ссылка в главе несёт класс `{.tall}`; остальные стоят в обычном поле 167 × 98 мм. Раскладка `graph` требует Graphviz 14.0.4, генератор при другой версии отказывает.

Проверку `book/check-figures.sh` для этой книги запускает сборка `a2a-book/build.sh` (она передаёт `BOOK_ROOT=a2a-book`). Правила проверки те же, что в `book/src/MANIFEST.md`. Отдельно: `BOOK_ROOT=a2a-book bash book/check-figures.sh` (оба прохода), `--structural` или `--render`.

**Происхождение.** «книга» — исходник ведёт эта книга. Копий из `sources/` нет.

| Рисунок | Исходник | Происхождение | SHA-256 копии | Поле | Главы |
| --- | --- | --- | --- | --- | --- |
| a2a-module-structure | `a2a-module-structure.toml` | книга | — | tall | Устройство модуля |
| a2a-publish-receive | `a2a-publish-receive.toml` | книга | — | tall | Устройство модуля |
| a2a-wake | `a2a-wake.toml` | книга | — | tall | Пробуждение |
