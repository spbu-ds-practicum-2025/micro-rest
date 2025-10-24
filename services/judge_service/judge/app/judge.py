import docker
import asyncio
import tempfile
import os
#import resource
from typing import Dict, Any
import logging
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class PythonJudge:
    def __init__(self, docker_client, db_manager: DatabaseManager):
        self.docker_client = docker_client
        self.db_manager = db_manager

    async def evaluate_submission(self, user_id: int, task_id: int, code: str,
                                  time_limit: int = 5, memory_limit: int = 128) -> Dict[str, Any]:
        """Оценить отправленное решение"""

        # Сохраняем отправку в БД
        submission_id = self.db_manager.create_submission(
            user_id=user_id,
            task_id=task_id,
            code=code
        )

        try:
            # Создаем временный файл с решением
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file_path = f.name

            # Выполняем код в Docker контейнере
            result = await self._run_in_container(
                temp_file_path,
                time_limit,
                memory_limit
            )

            # Обновляем запись в БД
            self.db_manager.update_submission(
                submission_id=submission_id,
                status=result['status'],
                execution_time=result.get('execution_time'),
                memory_used=result.get('memory_used'),
                error_message=result.get('error_message')
            )

            return {
                "submission_id": submission_id,
                **result
            }

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            self.db_manager.update_submission(
                submission_id=submission_id,
                status="error",
                error_message=str(e)
            )
            raise

        finally:
            # Удаляем временный файл
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)

    async def _run_in_container(self, file_path: str, time_limit: int, memory_limit: int) -> Dict[str, Any]:
        """Запустить код в Docker контейнере"""

        container = None
        try:
            # Создаем контейнер с ограничениями
            container = self.docker_client.containers.create(
                image="python:3.9-slim",
                command=f"timeout {time_limit}s python /solution/solution.py",
                volumes={
                    os.path.dirname(file_path): {
                        'bind': '/solution',
                        'mode': 'ro'
                    }
                },
                working_dir="/solution",
                mem_limit=f"{memory_limit}m",
                cpu_period=100000,
                cpu_quota=int(time_limit * 100000),
                network_disabled=True,  # Отключаем сеть для безопасности
                read_only=True,  # Только чтение
            )

            # Запускаем контейнер
            container.start()

            # Ждем завершения с таймаутом
            try:
                result = container.wait(timeout=time_limit + 2)
                exit_code = result['StatusCode']

                # Получаем логи
                logs = container.logs().decode('utf-8')

            except Exception as e:
                container.stop()
                return {
                    "status": "time_limit_exceeded",
                    "error_message": f"Execution time exceeded {time_limit} seconds"
                }

            # Анализируем результат
            if exit_code == 0:
                return {
                    "status": "success",
                    "execution_time": self._extract_execution_time(logs),
                    "memory_used": self._estimate_memory_usage(container)
                }
            elif exit_code == 124:  # timeout exit code
                return {
                    "status": "time_limit_exceeded",
                    "error_message": f"Execution time exceeded {time_limit} seconds"
                }
            else:
                return {
                    "status": "runtime_error",
                    "error_message": logs[-1000:]  # Последние 1000 символов логов
                }

        except docker.errors.ContainerError as e:
            return {
                "status": "runtime_error",
                "error_message": str(e)
            }
        except Exception as e:
            return {
                "status": "system_error",
                "error_message": str(e)
            }
        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass

    def _extract_execution_time(self, logs: str) -> float:
        """Извлечь время выполнения из логов"""
        # Здесь можно добавить парсинг времени выполнения
        # Пока возвращаем приблизительное значение
        return 0.0

    def _estimate_memory_usage(self, container) -> int:
        """Оценить использование памяти"""
        try:
            stats = container.stats(stream=False)
            memory_stats = stats['memory_stats']
            if 'usage' in memory_stats:
                return memory_stats['usage']
            return 0
        except:
            return 0