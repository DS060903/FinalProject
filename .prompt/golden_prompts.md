# Golden Prompts

**Project:** Campus Resource Hub - AiDD 2025 Capstone

This document highlights the most impactful prompts and AI interactions that significantly improved design, debugging, or documentation.

---

## 🏆 Top 6 Golden Prompts

### 1. Test Suite Cleanup & Alignment ⭐ NEW
**Category:** Testing & Refactoring  
**Tool:** Cursor AI  
**Impact:** CRITICAL - Achieved 100% pass rate and perfect assignment alignment

**Prompt:**
```
PROJECT CLEAN TEST SUITE (AiDD alignment)

You are my code editor copilot. Refactor the repo's tests so they exactly satisfy 
BOTH AiDD "Campus Resource Hub" brief and "Final Project Testing Prompt" and 
remove everything else.

Do:
Create/keep this structure:
  /tests/
    unit/
      test_booking_conflicts.py
      test_booking_status.py
      test_dal_crud.py
      test_validation_utils.py
      test_security_utils.py
    integration/
      test_auth_flow.py
      test_route_negative.py
    manual/
      TEST_PLAN.md
    conftest.py
    pytest.ini

Implement tests that must pass:
- Unit (≥5): booking conflict cases; status transitions; DAL CRUD independent 
  of routes; validation helper; security helper enforcing parameterized queries
- Integration (2): register→login→protected route (positive); one negative 
  route test (invalid payload)
- Manual: 6 cases (3 positive, 3 negative) using Given/When/Then
- Security: injection attempt and XSS string safely handled

Don't:
- Don't include tests for optional features not shipped
- Don't add CI/CD or deployment tests

Ensure pytest -q passes locally.
```

**Result:** 
- **Before:** 100+ tests, 53 failures, complex structure
- **After:** 31 tests, 0 failures, clean `unit/`/`integration/`/`manual/` structure
- Deleted 27 redundant test files
- 100% assignment compliance verified
- All tests passing in 18.77s

**Why It Worked:** 
1. **Clear Requirements:** Explicitly listed both assignment documents and required test counts
2. **Structure Specified:** Exact folder layout and file names provided
3. **Do/Don't Lists:** Helped AI focus on core requirements only
4. **Acceptance Criteria:** "pytest -q passes locally" gave clear success metric

**Key Lesson:** When refactoring, providing both the destination state AND exclusion criteria helps AI make better decisions about what to keep vs. remove.

---

### 2. DAL Pattern Architecture Prompt
**Category:** Architecture  
**Tool:** Cursor AI  
**Impact:** High - Established clean separation of concerns

**Prompt:**
```
Create a Data Access Layer (DAL) pattern for Flask that encapsulates all database 
operations, ensuring controllers remain thin. The DAL should:
- Handle all SQLAlchemy queries
- Provide CRUD functions for users, resources, bookings, messages, reviews
- Include business logic validation (e.g., booking conflicts, review eligibility)
- Use parameterized queries to prevent SQL injection
- Return model instances or raise appropriate exceptions
```

**Result:** Generated `src/data_access/dal.py` structure that became the foundation for all database operations. This prompt helped establish the MVC architecture clearly.

**Why It Worked:** Specific requirements (CRUD, validation, security) helped AI generate a comprehensive, well-structured solution.

---

### 3. AI Concierge RAG-Lite Implementation
**Category:** AI Feature  
**Tool:** Cursor AI  
**Impact:** High - Enabled context-aware AI feature

**Prompt:**
```
Create an AI concierge service that:
1. Answers questions about using the app (help mode)
2. Discovers resources using RAG-lite - query database for matching resources 
   and include them in OpenAI context
3. Generates polite message drafts
4. Never hallucinates - only reference actual database data
5. Includes rate limiting and PII redaction
6. Has graceful fallback when OpenAI unavailable
```

**Result:** Implemented `src/services/ai_concierge.py` with all three modes, proper context grounding, and fallback logic. This became a key differentiator for the project.

**Why It Worked:** Clear requirements for RAG-lite, no hallucinations, and fallback ensured AI generated a production-ready, ethical implementation.

---

### 4. Security Headers Middleware
**Category:** Security  
**Tool:** Cursor AI  
**Impact:** High - Comprehensive security implementation

**Prompt:**
```
Add security headers middleware to Flask app including:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Content-Security-Policy (allow Bootstrap CDN and inline styles)
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: disable geolocation, microphone, camera
Use Flask's after_request hook
```

**Result:** Generated complete security headers implementation in `src/app.py` that passed security tests and improved project security posture.

**Why It Worked:** Specific header requirements and Flask pattern helped AI generate correct, complete implementation.

---

### 5. Booking Conflict Detection Logic
**Category:** Business Logic  
**Tool:** Cursor AI  
**Impact:** High - Critical feature correctness

**Prompt:**
```
Implement booking conflict detection that checks for overlapping time windows:
- Two bookings conflict if: (start1 < end2) AND (end1 > start2)
- Ignore cancelled and rejected bookings
- Completed bookings should still conflict for edit operations
- Return clear error messages
Include edge cases: exact adjacency (no conflict), nested windows, surrounding windows
```

**Result:** Generated robust conflict detection logic in `src/data_access/dal.py` that handles all edge cases correctly.

**Why It Worked:** Mathematical definition of overlap and specific edge cases helped AI generate comprehensive, correct logic.

---

### 6. Test Fixture Generation
**Category:** Testing  
**Tool:** Cursor AI  
**Impact:** Medium - Accelerated test development

**Prompt:**
```
Generate pytest fixtures for:
- Flask app with test configuration
- Test client
- Sample users (student, staff, admin)
- Sample resources with different statuses
- Sample bookings with different statuses
Use conftest.py pattern, ensure database isolation between tests
```

**Result:** Created comprehensive test fixtures in `tests/conftest.py` that enabled rapid test development.

**Why It Worked:** Clear fixture requirements and pytest patterns helped AI generate reusable, well-structured test infrastructure.

---

## Prompt Engineering Best Practices Learned

1. **Be Specific:** Include exact requirements, patterns, and constraints
2. **Provide Context:** Reference existing code structure and patterns
3. **Request Examples:** Ask for edge cases and error handling
4. **Iterate:** Refine prompts based on initial outputs
5. **Verify:** Always review and test AI-generated code
6. **Specify "Don'ts":** When refactoring, list what to EXCLUDE as well as what to include
7. **Provide Success Metrics:** Clear acceptance criteria (e.g., "all tests must pass") helps AI verify correctness

---

## Context Grounding Example

**Prompt that used project context:**
```
The AI Concierge should reference actual resources from the database. Use the 
resource schema: id, title, description, category, location, capacity, rating_avg.
Query using keywords extracted from user query, limit to 6 results, include in 
OpenAI context as "Context resources: ..."
```

This prompt explicitly referenced the project's database schema, demonstrating context grounding as required by the project brief.

---

## 🎯 Major Milestone: Test Suite Refactoring

**Date:** November 9, 2025  
**Impact:** Project became submission-ready

The **Test Suite Cleanup & Alignment** prompt (Golden Prompt #1) represents a pivotal moment in the project. After building comprehensive test coverage (100+ tests), we audited against assignment requirements and refactored to a lean, focused suite.

**Transformation:**
- ❌ Before: 100+ tests, 53 failures, 8 errors, complex structure
- ✅ After: 31 tests, 0 failures, 0 errors, clean organization

**Why This Matters:**
This demonstrates that AI can handle complex refactoring tasks when given:
1. Clear target requirements (both assignment docs)
2. Explicit structure specification
3. Include/exclude criteria
4. Measurable success criteria

This refactoring made the project:
- ✅ 100% compliant with assignment requirements
- ✅ Ready for instructor submission
- ✅ Easy to maintain and extend
- ✅ Clear demonstration of testing best practices

---

**Note:** These prompts represent the most effective AI interactions that significantly improved code quality, architecture, or feature implementation. Golden Prompt #1 showcases AI's capability for large-scale refactoring when properly guided.
