# Manual Test Plan

**⚠️ Note**: The canonical manual test plan is now located at **`tests/manual/TEST_PLAN.md`**.

This document is kept for historical reference and context for AI tools.

---

## Quick Reference

The manual test plan includes **6 test cases** (3 positive, 3 negative) covering:

**Positive Tests:**
1. Student books available resource
2. Admin approves pending booking  
3. User leaves review after completed booking

**Negative Tests:**
4. User attempts to book with end time before start time
5. Student attempts to access Admin Dashboard (403 Forbidden)
6. User attempts SQL injection in search field

**Full test plan with Given/When/Then steps**: [`tests/manual/TEST_PLAN.md`](../../../tests/manual/TEST_PLAN.md)

---

## Compliance

✅ Meets AiDD Final Project Testing requirements:
- 6 test cases (3 positive, 3 negative)
- Given/When/Then format
- Step-by-step actions
- Expected results
- Status tracking columns

---

## Running Manual Tests

### Prerequisites
```bash
# Seed demo data
cd "C:\Users\Dewang Sethi\Downloads\Final proj"
.\.venv\Scripts\python.exe -m flask --app src.app seed

# Run Flask app
.\.venv\Scripts\python.exe -m flask --app src.app run
```

### Test Users
- **Student**: `student@demo.edu` / `Student123!`
- **Admin**: `admin@demo.edu` / `Admin123!`
- **Staff**: `staff@demo.edu` / `Staff123!`

---

*For the complete manual test plan, see [`tests/manual/TEST_PLAN.md`](../../../tests/manual/TEST_PLAN.md)*

