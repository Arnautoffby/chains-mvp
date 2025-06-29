## [2025-06-30] - Система слотов и уровней
### Добавлено
- Slots table with slots_total/slots_filled fields and SlotStatus Enum
- chains.py service: slot creation, reservation, activation, and auto-expiration
- /myteam command and inline button for slot deletion
- Background task to clean slots every 10 minutes
- Initial Alembic migration 20250629_00 with full schema

### Изменено
- bot/main.py: connected team router and background task
- docker-compose.yml: removed custom command, using CMD from Dockerfile
- docs/tasktracker.md updated

### Исправлено
- Incorrect payment calculation in status handler
- Alembic migration conflicts (merged into initial migration)

