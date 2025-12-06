import os
import subprocess
import tempfile
from typing import List, Tuple

from .models import TestCase

# Простой лимит времени на один тест
TIME_LIMIT_SECONDS = 2.0

# Все задачи считаем по 100 баллов
FULL_SCORE = 100


def run_python_code_against_tests(
    code: str, test_cases: List[TestCase]
) -> Tuple[bool, int]:
    """
    Запускает данный код на всех тестах.
    Возвращает (все_ли_пройдены, набранный_балл).
    """

    if not test_cases:
        # Нет тестов — считаем, что всё ок, балл 0 (можно сделать 100, если хочется)
        return True, 0

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        all_passed = True

        for test in test_cases:
            try:
                proc = subprocess.run(
                    ["python", tmp_path],
                    input=test.input_data,
                    capture_output=True,
                    text=True,
                    timeout=TIME_LIMIT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                all_passed = False
                break

            if proc.returncode != 0:
                all_passed = False
                break

            stdout = proc.stdout

            if stdout.rstrip() != test.expected_output.rstrip():
                all_passed = False
                break

        score = FULL_SCORE if all_passed else 0
        return all_passed, score
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
