# Test Suite — Campus Resource Hub

**Clean, minimal, and 100% aligned with AiDD assignment requirements.**

---

## 📁 Structure

```
tests/
├── unit/                           # White-box unit tests
│   ├── test_booking_conflicts.py  # Conflict detection logic
│   ├── test_booking_status.py     # Status transition rules
│   ├── test_dal_crud.py            # DAL CRUD operations (DB-independent)
│   ├── test_security_utils.py      # SQL injection prevention, sanitization
│   └── test_validation_utils.py    # Input validation helpers
├── integration/                    # Black-box integration tests
│   ├── test_auth_flow.py           # Register → Login → Protected route
│   └── test_route_negative.py      # Invalid payloads, error handling
├── manual/                         # Manual test plan
│   └── TEST_PLAN.md                # 6 scenarios (3 positive, 3 negative)
├── conftest.py                     # Shared fixtures (app, client, DB)
└── pytest.ini                      # Pytest configuration

```

---

## ✅ Test Coverage

### **Unit Tests (13 tests)**
- **Booking Conflicts** (3 tests): Overlapping, non-overlapping, adjacent time windows
- **Booking Status** (5 tests): Valid/invalid state transitions (pending → approved, rejected, etc.)
- **DAL CRUD** (7 tests): User, Resource, Booking create/read/update operations (independent of Flask routes)
- **Validation** (7 tests): Pagination, time windows, date ranges
- **Security** (5 tests): SQL injection prevention, text sanitization

### **Integration Tests (4 tests)**
- **Auth Flow** (2 tests): Full register → login → protected route flow
- **Negative Routes** (2 tests): Invalid booking dates, missing required fields

### **Manual Tests (6 cases)**
- **Positive**: Student books resource, admin approves, user leaves review
- **Negative**: Invalid dates, unauthorized access, SQL injection attempt

---

## 🚀 Running Tests

### Run all tests
```bash
pytest tests/ -q
```

### Run specific categories
```bash
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
```

### Generate coverage report
```bash
pytest tests/ --cov=src --cov-report=term
```

---

## 📊 Current Status

✅ **31 tests passing**  
✅ **0 failures**  
⚠️ **249 warnings** (deprecation warnings from libraries - not errors)

---

## 🎯 Assignment Compliance

| Requirement | Status | Location |
|-------------|--------|----------|
| ≥5 unit tests | ✅ **13 tests** | `tests/unit/` |
| ≥2 integration tests | ✅ **4 tests** | `tests/integration/` |
| DAL unit test (independent of routes) | ✅ | `tests/unit/test_dal_crud.py` |
| Security: SQL injection test | ✅ | `tests/unit/test_security_utils.py` |
| 6 manual test cases (3+/3-) | ✅ | `tests/manual/TEST_PLAN.md` |
| All tests pass locally | ✅ | `pytest tests/ -q` |

---

## 📝 Notes

- **No CI/CD or deployment tests** (not required by assignment)
- **No tests for optional features** (calendar sync, waitlists, analytics)
- **Focused on core Campus Resource Hub requirements**: booking, auth, DAL, security
- **All tests use temp SQLite database** (`:memory:` or temp file)

---

*Last updated: November 9, 2025*

