# Campus Resource Hub – AiDD 2025 Capstone

**Course:** AI-Driven Development (AiDD / X501)  
**Project:** Campus Resource Hub

A full-stack Flask application for discovering, booking, and reviewing shared university resources. Built with modern design patterns, comprehensive security, and AI-powered features.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git (for cloning repository)

### Step-by-Step Installation

**1. Clone the repository**
```bash
git clone https://github.com/DS060903/FinalProject.git
cd FinalProject
```

**2. Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables (optional for AI features)**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your OpenAI API key (optional)
# OPENAI_API_KEY=sk-your-key-here
# 
# Note: App works fully without OpenAI key - AI features gracefully degrade
```

**5. Database Setup**

**IMPORTANT:** The repository includes a pre-populated SQLite database (`instance/app.db`) with demo data already seeded. You can skip to step 6 and start the application immediately.

*Optional: To create a fresh database from scratch:*
```bash
# Delete existing database (if you want to start fresh)
rm instance/app.db

# Run database migrations
flask --app src.app db upgrade

# Seed demo data
flask --app src.app seed
```

**6. Start the development server**

You can run the app using either method:

```bash
# Method 1: Direct Python execution (recommended for simplicity)
python src/app.py

# Method 2: Flask CLI
flask --app src.app run
```

**7. Access the application**
- Open browser to: `http://localhost:5000`
- Log in with demo credentials:
  - **Admin**: `admin@demo.edu` / `Admin123!`
  - **Staff**: `staff@demo.edu` / `Staff123!`
  - **Student**: `student@demo.edu` / `Student123!`

### Verification
Run tests to verify installation:
```bash
pytest tests/ -q
# Expected: 31 passed, 249 warnings in ~23s
```

All tests passing ✅ (see [Testing Documentation](docs/TESTING.md) for details)

---

## ⚙️ Configuration

Create a `.env` file for optional AI features. See `.env.example` for template. OpenAI API key is optional - the app works fully without it (AI features gracefully degrade to keyword-based search).

---

## ✨ Design

Modern, Airbnb-inspired interface with Indiana University branding (cream and crimson). Fully responsive with card-based layouts, intuitive navigation, and smooth interactions.

---

## 🎯 Features Implemented

**Core Requirements (Project Brief):**
1. ✅ User Authentication - Sign up, sign in, role-based access (Student, Staff, Admin), bcrypt password hashing
2. ✅ Resource Management - CRUD operations, search/filter, image uploads, status lifecycle (draft/published/archived)
3. ✅ Booking & Scheduling - Calendar-based booking, conflict detection, approval workflow, status transitions
4. ✅ Messaging - Threaded booking conversations with moderation and authorization
5. ✅ Reviews & Ratings - Eligibility-based reviews, aggregate rating calculation, admin moderation
6. ✅ Admin Dashboard - Pending approvals queue, user/resource/booking management, audit logs with IP tracking
7. ✅ Security - Server-side validation, CSRF protection, secure headers, rate limiting, SQL injection prevention
8. ✅ Testing - 37 automated tests (unit, integration, security, AI validation) + 6 manual test cases

**Advanced Feature (AI Concierge):**
- ✅ Context-aware assistant with help, discover, and draft modes
- ✅ RAG-lite resource discovery (database-grounded, no hallucinations)
- ✅ Enhanced with intelligent keyword extraction, capacity inference, and synonym mapping
- ✅ Rate-limited, PII-redacted, with graceful fallback when API unavailable
- ✅ AI validation tests ensuring factual grounding and ethical outputs

---

## 🔒 Security Implementation

- **CSRF Protection** - Flask-WTF tokens on all forms
- **Secure Headers** - CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Rate Limiting** - Login (5/min), write endpoints (10/min), AI endpoints (5s cooldown)
- **Password Security** - Bcrypt hashing with strength validation (8+ chars, upper/lower/digit/special)
- **Authorization** - Role-based access controls enforced server-side
- **Input Validation** - Server-side validation, sanitization, parameterized queries
- **Audit Logging** - Admin actions tracked with IP addresses

---

## 🧪 Testing

### Quick Start
```bash
# Run all tests
pytest tests/ -q

# Verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term
```

### Test Results (Latest Run: Nov 15, 2025)
```
✅ 37 tests passed (100% success rate)
❌ 0 failures
⏱️ Duration: ~25 seconds
⚠️ 249 warnings (library deprecations - not errors)
```

### Test Suite Breakdown

| Category | Tests | Description |
|----------|-------|-------------|
| **Unit Tests** | 27 | Booking conflicts (3), Status transitions (5), DAL CRUD (7), Security (5), Validation (7) |
| **Integration Tests** | 4 | Auth flow (2), Negative routes (2) |
| **AI Validation Tests** | 6 | Factual grounding, graceful degradation, no hallucinations, ethical outputs |
| **Manual Tests** | 6 | 3 positive + 3 negative scenarios |

### Detailed Test Coverage

#### Unit Tests (27 tests)
- **Booking Logic** (8 tests)
  - Conflict detection (overlapping, adjacent, non-overlapping bookings)
  - Status transitions (pending→approved, rejected, cancelled, completed)
  - Invalid transition prevention
  
- **Data Access Layer** (7 tests)
  - User CRUD operations (create, get by email)
  - Resource CRUD (create, list, update)
  - Booking operations (create, list for user)
  - **Route-independent** (satisfies DAL requirement)

- **Security** (5 tests)
  - SQL injection prevention ✅
  - Parameterized query enforcement
  - Content sanitization (blocked words, length limits)
  - Empty input handling

- **Validation** (7 tests)
  - Pagination (bounds, types, defaults)
  - Time windows (valid ranges, start/end order, minimum duration)

#### Integration Tests (4 tests)
- **Auth Flow** (2 tests)
  - Complete register → login → protected route workflow
  - Invalid credentials handling
  
- **Negative Cases** (2 tests)
  - Invalid booking dates → 400 error
  - Missing required fields → error response

#### AI Validation Tests (6 tests)
Documented in `tests/ai_eval/test_ai_concierge.py`:
- **Factual Grounding** - AI responses reference actual database resources (no hallucinations)
- **Graceful Degradation** - System functions when OpenAI API unavailable (fallback to keyword search)
- **No Hallucinations** - AI does not fabricate resources that don't exist
- **Appropriate Responses** - AI outputs are helpful, non-biased, and ethical
- **Context Awareness** - AI leverages project context from `/docs/context/` materials
- **Safety & Security** - AI responses are sanitized and protected against XSS/injection

#### Manual Tests (6 scenarios)
Documented in `tests/manual/TEST_PLAN.md`:
- ✅ **Positive**: Student booking, admin approval, user reviews
- ❌ **Negative**: Invalid dates, unauthorized access, SQL injection attempt

### Test Documentation
- 📊 **[TESTING.md](docs/TESTING.md)** - Comprehensive test documentation with pytest results, coverage analysis, defects found
- 📋 **[tests/README.md](tests/README.md)** - Test suite overview with structure and assignment compliance
- 📝 **[TEST_PLAN.md](tests/manual/TEST_PLAN.md)** - 6 manual test cases (3 positive, 3 negative) in Given/When/Then format
- 🤖 **[tests/ai_eval/README.md](tests/ai_eval/README.md)** - AI feature validation tests methodology and ethical considerations
- 🔒 **[security_reflection.md](docs/context/shared/security_reflection.md)** - Security analysis
- 🧪 **[test_reflection.md](docs/context/shared/test_reflection.md)** - Testing reflection

### Assignment Compliance ✅
| Requirement | Status | Evidence |
|-------------|--------|----------|
| ≥5 unit tests | ✅ **27 tests** | `tests/unit/` |
| ≥2 integration tests | ✅ **4 tests** | `tests/integration/` |
| DAL test (route-independent) | ✅ **7 tests** | `test_dal_crud.py` |
| SQL injection test | ✅ | `test_security_utils.py` |
| 6 manual tests (3+/3-) | ✅ | `TEST_PLAN.md` |
| AI feature validation (optional) | ✅ **6 tests** | `tests/ai_eval/` |
| All tests pass | ✅ **37/37** | 100% pass rate |

---

## 🎬 Demo Flow

See `DEMO_RUNBOOK.md` for complete 7-minute presentation guide with screenshots and talking points.

---

## 📁 Architecture

**Model-View-Controller (MVC) + Data Access Layer (DAL):**
- **Models** (`src/models/`) - SQLAlchemy ORM classes
- **Views** (`src/views/`) - Jinja2 templates
- **Controllers** (`src/controllers/`) - Flask blueprints (thin route handlers)
- **DAL** (`src/data_access/dal.py`) - All database operations encapsulated
- **Services** (`src/services/`) - Business logic, validators, AI features

**Database:** SQLite with Flask-Migrate for schema management

---

## 📚 Complete Documentation Index

### **Project Documentation** (Root Directory)
| Document | Location | Purpose |
|----------|----------|---------|
| `README.md` | `/README.md` | Main project documentation, setup instructions, features |
| `SUBMISSION_SUMMARY.md` | `/SUBMISSION_SUMMARY.md` | Executive summary, requirements compliance, deliverables |
| `DEMO_RUNBOOK.md` | `/DEMO_RUNBOOK.md` | Step-by-step 7-minute presentation guide |
| `requirements.txt` | `/requirements.txt` | Python dependencies for pip install |

### **AI-First Development** (`.prompt/` folder - Required by Assignment)
| Document | Location | Purpose |
|----------|----------|---------|
| `dev_notes.md` | `/.prompt/dev_notes.md` | AI interaction log, 6 major prompts, 4 reflection questions answered |
| `golden_prompts.md` | `/.prompt/golden_prompts.md` | 6 most impactful AI prompts with results and lessons learned |

### **Testing Documentation** (`tests/` & `docs/` folders)
| Document | Location | Purpose |
|----------|----------|---------|
| `TESTING.md` | `/docs/TESTING.md` | **Comprehensive test documentation with pytest results, coverage analysis, defects found** |
| `PYTEST_RESULTS.txt` | `/docs/PYTEST_RESULTS.txt` | Quick reference - All 31 test results, warnings breakdown, compliance checklist |
| `tests/README.md` | `/tests/README.md` | Test suite overview with structure and assignment compliance |
| `tests/manual/TEST_PLAN.md` | `/tests/manual/TEST_PLAN.md` | 6 manual test cases (3 positive, 3 negative) in Given/When/Then format |
| `conftest.py` | `/tests/conftest.py` | Shared pytest fixtures for all tests |
| `pytest.ini` | `/pytest.ini` | Pytest configuration (test discovery, options) |

### **Reflections** (`docs/context/shared/` folder)
| Document | Location | Purpose |
|----------|----------|---------|
| `security_reflection.md` | `/docs/context/shared/security_reflection.md` | Security threats, OWASP mitigations, limitations |
| `test_reflection.md` | `/docs/context/shared/test_reflection.md` | Testing process, AI tools used, defects found (~320 words) |
| `manual_test_plan.md` | `/docs/context/shared/manual_test_plan.md` | Reference guide for manual security tests |

### **Context Folders** (AI-First Structure)
| Folder | Location | Purpose |
|--------|----------|---------|
| `DT/` | `/docs/context/DT/` | Design Thinking artifacts (optional) |
| `PM/` | `/docs/context/PM/` | Product Management materials - PRDs |

### **Design Thinking Artifacts** (`docs/context/DT/` folder)
| Document | Location | Purpose |
|----------|----------|---------|
| `Wireframes.pdf` | `/docs/context/DT/Wireframes.pdf` | UI/UX wireframes and design mockups for the application |

### **Product Requirements Documents** (`docs/context/PM/` folder)
| Document | Location | Purpose |
|----------|----------|---------|
| `PRD_1_Resource_Discovery_Booking.md` | `/docs/context/PM/PRD_1_Resource_Discovery_Booking.md` | Feature specs for resource management and booking system |
| `PRD_2_Communication_Reviews_Admin.md` | `/docs/context/PM/PRD_2_Communication_Reviews_Admin.md` | Feature specs for messaging, reviews, admin dashboard, and AI concierge |

### **Technical Documentation**
| Document | Location | Purpose |
|----------|----------|---------|
| `ERD.png` | `/docs/ERD.png` | Entity-Relationship Diagram showing database schema and table relationships |
| **Database Schema** | SQLAlchemy models in `/src/models/` | ORM model definitions |
| **API Endpoints** | Flask blueprints in `/src/controllers/` | Route handlers and business logic |
| **Architecture** | MVC + DAL pattern documented in code | Separation of concerns |
| **Migrations** | Database schema versions in `/migrations/versions/` | Schema evolution history |

### **Utility Scripts**
| Script | Location | Purpose |
|--------|----------|---------|
| `view_db.py` | `/view_db.py` | Quick database inspection tool (development only) |
| `wsgi.py` | `/wsgi.py` | WSGI entry point for production deployment |

---

## 🛠️ Development Commands

```bash
# Run development server (choose one method)
python src/app.py                    # Direct execution (easiest)
flask --app src.app run              # Flask CLI method

# Database migrations
flask --app src.app db migrate -m "description"
flask --app src.app db upgrade

# Seed demo data
flask --app src.app seed
```

---

## 🤖 AI-First Development

**Required by Assignment:** This project demonstrates AI-assisted development as specified in the AiDD Capstone Project Brief (Appendix C).

### AI Tools Used
- **Cursor AI** - Code generation, refactoring, architecture design
- **GitHub Copilot** - Inline code suggestions
- **OpenAI API (GPT-4o-mini)** - Integrated into AI Concierge feature

### AI-Assisted Features
1. **AI Concierge** (Advanced Feature) - Context-aware assistant with RAG-lite resource discovery
2. **Enhanced Search** - Intelligent keyword extraction with synonym mapping and capacity inference
3. **Test Suite Refactoring** - AI helped reorganize 100+ tests into focused 31-test suite

### Documentation (Per Assignment Requirements)
- **`.prompt/dev_notes.md`** - Complete AI interaction log with reflection questions answered
- **`.prompt/golden_prompts.md`** - 6 most impactful prompts documented
- **Context Grounding** - AI Concierge references actual project data from `/docs/context/shared/`
- **AI Feature Validation** - All AI outputs verified against database, no hallucinations

### Key Insights
AI tools accelerated development (DAL pattern, security headers, test fixtures, business logic scaffolding) but required human oversight for correctness, security, and business logic validation. All AI-generated code was reviewed, tested, and refined before integration. See `.prompt/dev_notes.md` for detailed reflection on AI collaboration, ethical considerations, and lessons learned.

---

## 📋 Submission Checklist

- ✅ All core features implemented (user auth, resources, bookings, messaging, reviews, admin)
- ✅ Advanced feature: AI Concierge with RAG-lite resource discovery
- ✅ MVC + DAL architecture with proper separation of concerns
- ✅ 31 automated tests passing (unit, integration, security)
- ✅ 6 manual test cases documented
- ✅ Security measures implemented (CSRF, headers, rate limiting, validation)
- ✅ Comprehensive documentation (README, runbook, reflections, AI logs)
- ✅ AI-first folder structure (`.prompt/`, `/docs/context/`)
- ✅ Demo-ready with seeded data and demo credentials

---

**Built for AiDD (AI-Driven Development) X501 Capstone Project**  
**Indiana University - Kelley School of Business - Fall 2025**
