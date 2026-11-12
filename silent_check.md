# silent-check: детектор тихой валидности в агентных пайплайнах

Три эвристики по классам silent-but-valid (см. README):
1. zero-dispersion: серия артефактов JSON с нулевой дисперсией ключевых
   метрик = вероятный тихий дефолт конфигурации.
2. zero-runs: у ветки с недавним пушем нет ни одного CI-рана = вероятно,
   merge-ref конфликт, а не спокойствие.
3. tests-touched: дифф ветки правит файлы тестов = флаг для ревью
   (агент мог ослабить проверку).

Выход: JSON-отчёт + exit code (0 чисто, 1 найден сигнал тишины,
2 использование). Инструмент advisory: он не доказывает дефект,
он указывает, где сигнала нет.

## Использование

    python3 silent_check.py dispersion <artifacts-dir> <metric-key...>
    python3 silent_check.py runs <repo> <branch>
    python3 silent_check.py touched [base]

Примеры на реальных кейсах — в repro/.
