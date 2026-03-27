# Auto Grafik

Уеб инструмент за автоматично генериране на месечен график на служители с `FastAPI` backend, `OR-Tools CP-SAT` solver и `React + Vite` frontend.

## Структура

```text
auto_grafik/
  backend/
  frontend/
```

## Backend стартиране

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API ще бъде налично на `http://localhost:8000`.

## Frontend стартиране

```bash
cd frontend
npm install
npm run dev
```

Frontend ще бъде наличен на `http://localhost:5173`.

## Solver time limit

- solver-ът използва `max_time_in_seconds = 10` по подразбиране;
- допустимият работен диапазон е `5-15` секунди;
- настройката е дефинирана в `backend/app/core/config.py`.

## Strict и Best Effort

- `strict mode`: използва само основните служители и допуска само решения без hard нарушения;
- `best effort mode`: включва cover employee и допуска ограничено превишаване на нормата до 8%;
- `fallback best effort`: ако и това не стигне, solver-ът релаксира hard constraints чрез penalty променливи и връща най-доброто възможно решение с ясно маркирани нарушения.

## Примерен request payload

```json
{
  "month": 4,
  "year": 2026,
  "norm_hours": 168,
  "shifts": [
    {"id": "A2", "type": "day", "start_time": "07:00", "end_time": "19:00", "duration_hours": 12},
    {"id": "A3", "type": "night", "start_time": "19:00", "end_time": "07:00", "duration_hours": 12}
  ],
  "employees": [
    {"id": "e1", "name": "Ivan", "role": "Operator", "start_day": 1, "first_shift": "A2", "is_cover": false},
    {"id": "e2", "name": "Maria", "role": "Operator", "start_day": 1, "first_shift": "A3", "is_cover": false},
    {"id": "e3", "name": "Niki", "role": "Operator", "start_day": 2, "first_shift": "A2", "is_cover": false},
    {"id": "e4", "name": "Raya", "role": "Operator", "start_day": 3, "first_shift": "A3", "is_cover": false},
    {"id": "e5", "name": "Mila", "role": "Operator", "start_day": 4, "first_shift": "A2", "is_cover": false},
    {"id": "c1", "name": "Cover", "role": "Reserve", "start_day": 1, "first_shift": "A3", "is_cover": true}
  ]
}
```

## Примерен response

```json
{
  "schedule": [{"employee_id": "e1", "employee_name": "Ivan", "day": 1, "shift_id": "A2"}],
  "hard_violations": [],
  "soft_violations": [{"code": "below_preferred_hours", "message": "Employee Ivan is below the preferred 85% hours threshold.", "employee_id": "e1", "day": null, "shift_id": null, "severity": "soft"}],
  "employee_stats": [{"employee_id": "e1", "employee_name": "Ivan", "role": "Operator", "total_hours": 144, "total_shifts": 12, "day_shifts": 6, "night_shifts": 6, "consecutive_night_pairs": 0, "assignments_by_day": {"1": "A2"}, "is_cover": false}],
  "score": 97,
  "is_valid": true,
  "used_cover_employee": false,
  "used_best_effort": false,
  "explanation": "Strict mode found a fully valid schedule with no hard-constraint violations."
}
```

## Solver модел

Hard constraints:
- точно една дневна и една нощна смяна на ден;
- максимум една смяна на служител на ден;
- без смени преди `start_day`;
- задължителен `first_shift` на `start_day`;
- минимум 12 часа почивка между последователни смени;
- максимум 4 поредни работни дни;
- минимум 36 часа възстановяване след 4-дневна серия;
- максимум месечна норма в strict режима.

Soft constraints:
- penalty за небалансирани day/night смени;
- penalty за поредни нощни смени;
- penalty за отклонение от равномерно разпределение;
- penalty за недостатъчни часове под 85% от нормата;
- penalty за превишение на нормата в best effort режим.

Детерминизъм:
- `num_search_workers = 1`;
- `random_seed = 0`;
- стабилен tie-break по фиксиран ред на служители, дни и смени.

## Тестове

```bash
cd backend
pytest
```
