# Campus Resource Hub – Final Submission

**Course:** AI-Driven Development (AiDD / X501)  
**Institution:** Indiana University - Kelley School of Business  
**Term:** Fall 2025

---

## 📊 Project Overview

Full-stack Flask application enabling university departments and students to list, share, and reserve campus resources (study rooms, equipment, spaces).

**Technology Stack:**
- **Backend:** Python 3.13, Flask 3.0, SQLAlchemy, SQLite
- **Frontend:** Bootstrap 5, Jinja2 templates, custom CSS
- **AI Integration:** OpenAI API (GPT-4o-mini) for AI Concierge
- **Security:** Flask-WTF CSRF, secure headers, bcrypt, rate limiting
- **Testing:** Pytest (31 tests, 100% pass rate)

---

## ✅ Requirements Compliance

**Core Features (All Implemented):**
1. ✅ User authentication with role-based access (Student, Staff, Admin)
2. ✅ Resource CRUD operations with search, filter, image uploads
3. ✅ Booking workflow with conflict detection and approval system
4. ✅ Threaded messaging with moderation capabilities
5. ✅ Review & rating system with eligibility validation
6. ✅ Admin dashboard with audit logging
7. ✅ Server-side validation and security hardening
8. ✅ MVC + DAL architecture pattern

**Advanced Feature:**
✅ **AI Concierge** - Context-aware assistant with RAG-lite resource discovery, intelligent keyword extraction, and graceful fallback

**Non-Functional Requirements:**
✅ Server-side validation, CSRF protection, secure headers, rate limiting  
✅ Password security (bcrypt + strength validation)  
✅ SQL injection prevention (parameterized queries)  
✅ Role-based authorization enforced server-side

---

## 📦 Deliverables Included

**1. Codebase** - Fully functional Flask application
- Clean MVC + DAL architecture
- All core and advanced features implemented
- Production-ready security measures
- Comprehensive error handling and validation

**2. Documentation**
- `README.md` - Setup instructions, features, architecture, testing
- `DEMO_RUNBOOK.md` - 7-minute presentation guide
- `PITCH_NOTES.md` - 60-90 second pitch script
- `tests/README.md` - Test suite documentation
- `tests/manual/TEST_PLAN.md` - 6 manual test scenarios

**3. AI Development Artifacts**
- `.prompt/dev_notes.md` - AI interaction log + 4 reflection questions
- `.prompt/golden_prompts.md` - 6 most impactful AI prompts
- AI-first folder structure (`.prompt/`, `/docs/context/`)

**4. Reflections**
- `docs/context/shared/security_reflection.md` - Security analysis
- `docs/context/shared/test_reflection.md` - Testing strategy

---

## 🧪 Testing Summary

**Automated Tests:** ✅ **31/31 passing (0 failures)**

| Test Type | Count | Coverage |
|-----------|-------|----------|
| Unit Tests | 13 | Booking conflicts, status transitions, DAL CRUD, validation, security |
| Integration Tests | 4 | Auth flow (register→login→protected), negative routes |
| Security Tests | 5 | SQL injection, XSS prevention, parameterized queries |
| Validation Tests | 7 | Pagination, time windows, date ranges |
| Manual Test Cases | 6 | CSRF, rate limiting, CSP, booking validation, authz |

**Test Organization:**
- `tests/unit/` - White-box unit tests
- `tests/integration/` - Black-box integration tests  
- `tests/manual/TEST_PLAN.md` - Given/When/Then scenarios

**Assignment Compliance:**
✅ ≥5 unit tests (13 provided)  
✅ ≥2 integration tests (4 provided)  
✅ DAL CRUD test independent of routes  
✅ SQL injection prevention test  
✅ 6 manual test cases (3 positive, 3 negative)

---

## 🔐 Security Implementation

| Measure | Implementation |
|---------|----------------|
| **CSRF Protection** | Flask-WTF tokens on all forms |
| **Secure Headers** | CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| **Authentication** | Flask-Login with bcrypt password hashing |
| **Password Policy** | 8+ chars, uppercase, lowercase, digit, special character |
| **Authorization** | Role-based access (Student/Staff/Admin) enforced server-side |
| **Rate Limiting** | Login: 5/min, Write endpoints: 10/min, AI: 5s cooldown |
| **Input Validation** | Server-side validation, sanitization, length limits |
| **SQL Injection** | SQLAlchemy ORM with parameterized queries |
| **Session Security** | HttpOnly, SameSite=Lax, secure cookies in production |
| **Audit Logging** | Admin actions tracked with IP addresses |
| **PII Protection** | Redaction in AI prompts, minimal data collection |

---

## 💭 AI Development Reflections

**How did AI shape design decisions?**  
AI tools accelerated architectural scaffolding (DAL pattern, security headers, test fixtures) and helped explore implementation alternatives quickly. However, critical business logic, security measures, and user experience decisions were made by the team based on domain knowledge. AI excelled at structure and patterns, but human judgment remained essential.

**What did we learn about verifying AI outputs?**  
Verification is critical. Early in the project, we trusted AI outputs too quickly, leading to edge case bugs. We developed an iterative workflow: AI generates structure → team reviews → add edge case handling → add security checks → test thoroughly. AI tools don't understand our specific business rules, so domain knowledge was essential for refinement.

**Ethical considerations?**  
We maintained transparency by documenting all AI contributions in `.prompt/dev_notes.md` and marking significant AI-generated code. Attribution and accountability were key - while AI generated boilerplate, the team maintains full accountability. We also addressed bias in the AI Concierge by avoiding assumptions about user roles/capabilities.

**How might AI change business technologist roles?**  
The role shifts from "how to code" to "what to code and how to verify it." Technologists will spend less time on boilerplate and more on architecture, prompt engineering, quality assurance, and verification. Domain expertise becomes more valuable as AI can generate code but can't replace business process understanding.

See `.prompt/dev_notes.md` for complete reflections on all 4 assignment questions.

---

## 🏆 Key Achievements

1. **100% Test Pass Rate** - All 31 automated tests passing with comprehensive coverage
2. **Advanced AI Feature** - Context-aware concierge with RAG-lite (no hallucinations)
3. **Clean Architecture** - Proper MVC + DAL separation with encapsulated database access
4. **Production Security** - Multi-layered defense (CSRF, headers, rate limiting, validation)
5. **Complete Documentation** - README, runbook, reflections, AI logs all submission-ready

---

## 📁 Repository Structure

```
/src/
  controllers/     # Flask blueprints (routes)
  data_access/     # DAL - all database operations
  models/          # SQLAlchemy ORM models
  services/        # Business logic, validators, AI
  views/           # Jinja2 templates
  static/          # CSS, JS, images
  config/          # Configuration management

/tests/
  unit/            # Unit tests (13 tests)
  integration/     # Integration tests (4 tests)
  manual/          # Manual test plan (6 scenarios)
  conftest.py      # Shared pytest fixtures

/.prompt/
  dev_notes.md     # AI interaction log + reflections
  golden_prompts.md # 6 most impactful prompts

/docs/context/
  shared/          # Reflections and test plans
  APA/             # (Optional - empty)
  DT/              # (Optional - empty)
  PM/              # (Optional - empty)

/migrations/       # Flask-Migrate database migrations
```

---

## 🚀 Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate (Windows)
pip install -r requirements.txt
cp .env.example .env
flask --app src.app db upgrade
flask --app src.app seed
flask --app src.app run
```

**Demo Credentials:**
- Admin: `admin@demo.edu` / `Admin123!`
- Staff: `staff@demo.edu` / `Staff123!`
- Student: `student@demo.edu` / `Student123!`

---

## 📊 Test Commands

```bash
# All tests
pytest -q

# Smoke tests only
pytest -q -k smoke

# Security tests only
pytest -q -k security

# With coverage
pytest --cov=src --cov-report=html
```

---

## ✅ Final Submission Checklist

| Requirement | Status | Location |
|-------------|--------|----------|
| Functional codebase | ✅ Complete | Entire repository |
| README with setup instructions | ✅ Complete | `/README.md` |
| requirements.txt | ✅ Complete | `/requirements.txt` |
| Database schema & migrations | ✅ Complete | `/migrations/`, models documented in code |
| .prompt/dev_notes.md | ✅ Complete | `/.prompt/dev_notes.md` |
| .prompt/golden_prompts.md | ✅ Complete | `/.prompt/golden_prompts.md` |
| AI-first folder structure | ✅ Complete | `/.prompt/`, `/docs/context/` |
| Test suite (all passing) | ✅ 31/31 passing | `/tests/` |
| Demo script | ✅ Complete | `/DEMO_RUNBOOK.md` |
| Reflections | ✅ Complete | `.prompt/dev_notes.md`, `/docs/context/shared/` |
| Core features (1-7) | ✅ All implemented | Verified via tests and manual review |
| Advanced feature | ✅ AI Concierge | `/src/services/ai_concierge.py` |
| MVC + DAL architecture | ✅ Properly separated | `/src/` structure |
| Security measures | ✅ All implemented | CSRF, headers, rate limiting, validation |

---

**Status:** ✅ **Submission Ready**  
**Last Updated:** November 2025  
**Course:** AiDD X501 - Indiana University

