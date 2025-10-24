# Сборка и запуск:
docker-compose up --build

# Проверка работы:
curl -X POST "http://localhost:8000/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "task_id": 1,
    "code": "print(\"Hello, World!\")",
    "time_limit": 5,
    "memory_limit": 128
  }'