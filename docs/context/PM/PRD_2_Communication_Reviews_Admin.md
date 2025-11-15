# Product Requirements Document (PRD)
# PRD 2: Communication, Reviews & Administration

**Project:** AiDD Campus Resource Hub  
**Document Version:** 1.0  
**Last Updated:** November 2024  
**Owner:** Product Management

---

## Feature 3: Messaging & Reviews System

### Context

Booking workflows require communication between requesters, owners, and administrators. Threaded messaging enables transparent communication; reviews help others make informed decisions.

### Problem Statement

Communication happens via email/external tools, creating fragmented conversations. Owners struggle to respond in context; requesters lack status visibility. After completion, no structured feedback; future users can't benefit from past experiences.

### Goals

- **Threaded messaging** within booking contexts (requester, owner, admin)
- **Message moderation** (hide/report inappropriate content)
- **Eligibility-based reviews** (completed bookings only)
- **Aggregate ratings** (average, review count per resource)
- **Unified inbox** for all threads
- **Track authorship** and timestamps

### Non-Goals

- Real-time chat
- Email integration
- Review replies
- Review editing (users can update existing reviews)

### Users & Flows

#### Students/Staff
- View booking detail with thread
- Send/receive messages
- Leave review after completion (rating 1-5, optional comment)
- Update existing review
- View all threads in "My Messages"

#### Owners (Staff/Admin)
- Receive/respond to messages
- View all bookings with threads
- See reviews for their resources

#### Admins
- Participate in any thread
- Moderate messages/reviews (hide/unhide)
- View all content

### Flow Summary

#### Messaging Flow

1. **View Thread**
   - User views booking detail (participant required: requester, owner, or admin)
   - Thread displayed chronologically

2. **Send Message**
   - User types message, clicks Send
   - System validates (non-empty, length, sanitization)
   - Message saved (booking_id, sender_id, content, timestamp, hidden=false)
   - Page refreshes with new message

3. **Moderation**
   - User reports OR admin reviews
   - Admin views reported content
   - Admin can hide (hidden=true, removed from public view)
   - Hidden messages visible only to admins
   - Thread shows "[Message hidden]" placeholder

4. **Authorization**
   - Only participants can view/send:
     - Requester (booking.user_id)
     - Owner (resource.created_by)
     - Admins (any thread)
   - Server-side checks enforce access

#### Reviews Flow

1. **Eligibility Check**
   - User must have COMPLETED booking for resource
   - System checks `user_has_completed_booking()`
   - **Eligible:** Form shown
   - **Not eligible:** Form hidden with message

2. **Submission**
   - User selects rating (1-5 stars)
   - Optional comment (max 2000 chars, sanitized)
   - System validates (rating 1-5, comment length)
   - **If already reviewed:** Update existing
   - Review saved (resource_id, user_id, rating, comment, timestamp, hidden=false)
   - Aggregate rating recalculated (average of non-hidden)
   - Review count updated

3. **Display**
   - Detail page shows average rating and count
   - Reviews listed chronologically
   - Each shows: rating, comment, reviewer name, date
   - Hidden reviews excluded from display

4. **Moderation**
   - Admin views all reviews
   - Can hide/unhide inappropriate reviews
   - Hidden reviews excluded from aggregate
   - Rating recalculated when hidden/unhidden

### UX & Metrics

#### UX Design

**Messaging:**
- Chat-like thread (messages aligned by sender)
- Timestamps for each message
- "My Messages" shows booking cards with last message preview
- Reply box at bottom of thread

**Reviews:**
- Review form inline on resource detail
- Star rating UI with numeric average display
- Review cards with user avatar placeholder
- Sort options (recent, highest rated)
- Empty states with CTAs ("Be the first to review!")

**Moderation:**
- Requires admin confirmation
- Reason field for hiding
- Audit trail of moderation actions

#### Success Metrics
- ≥40% of bookings have messages
- ≥50% of completed bookings generate reviews
- Average review length ≥20 words
- Moderation response time < 4 hours
- Ratings correlate with user satisfaction surveys

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Abusive messages | Sanitization, length limits, cooldowns, moderation tools |
| Review spam | Eligibility check prevents fake reviews; moderation catches violations |
| Rating manipulation | One review per user/resource; hidden reviews excluded from aggregate |
| Authorization bypass | Server-side checks on all endpoints |
| Performance | Paginate threads (50 messages/page); database indexing |

---

## Feature 4: Admin Dashboard & AI Concierge

### Context

Administrators need centralized oversight for operations, moderation, compliance, and support. Dashboard provides visibility; AI concierge enhances UX with contextual help, discovery, and drafting assistance.

### Problem Statement

Admins lack unified interface for approvals, moderation, and audits. Multiple tools cause delays. Users ask repetitive questions. Without automation and centralization, support burden increases.

### Goals

**Admin Dashboard:**
- Summary metrics (pending bookings, reported messages, hidden reviews)
- Manage users, resources, bookings, messages, reviews from single interface
- Log all critical actions (timestamp, actor, IP, details)
- Filter/search audit logs for investigations

**AI Concierge:**
- **Help mode:** Contextual guidance
- **Discover mode:** Resource suggestions
- **Draft mode:** Message composition assistance
- Database-grounded responses (no hallucinations)
- Graceful degradation when API unavailable

### Non-Goals

- Real-time analytics dashboards
- Automated decision-making
- External compliance reports
- Multi-tenant administration

### Users & Flows

#### Admins
- Access `/admin` (role-gated)
- View summary cards with key metrics
- Navigate to specialized views (bookings, users, resources, messages, reviews, logs)
- Approve/reject bookings
- Hide/unhide content
- Manage user roles
- Search logs (by user/IP/date/action)
- Export logs to CSV

#### All Users
- Access `/ai/assistant` (login required)
- Select mode (Help/Discover/Draft)
- Ask questions or provide prompts
- Receive AI responses with attribution
- Copy generated drafts

### Flow Summary

#### Admin Dashboard

1. **Main Dashboard**
   - Admin navigates to `/admin`
   - Summary cards display:
     - Pending bookings count
     - Reported messages count
     - Hidden reviews count
   - Cards link to detailed views
   - Recent actions feed (last 10 actions)

2. **Booking Management**
   - Admin views pending queue
   - List displays: booking ID, resource, requester, time, status, date
   - Each booking shows message thread
   - Admin clicks Approve/Reject with optional reason
   - System logs action (action, booking_id, admin_id, IP, timestamp)
   - Notification sent to requester

3. **User Management**
   - Admin views all users with role filter
   - List displays: email, role, join date, booking count
   - Admin views user details
   - Role changes logged and require confirmation

4. **Content Moderation**
   - Admin views reported/hidden content
   - List displays: content preview, reporter, date, context link
   - Admin can hide/unhide with reason
   - Action logged (content_id, admin_id, IP, timestamp)

5. **Audit Logging**
   - All critical actions logged via `log_admin_action()`
   - Log fields: action_type, resource_type, resource_id, description, admin_id, IP, timestamp
   - Admin views logs with filters (date range, user, action type, resource)
   - Paginated table view
   - CSV export for compliance

#### AI Concierge

**1. Help Mode**
- User asks: "How do I cancel a booking?"
- System uses OpenAI (GPT-4o-mini) with platform knowledge prompt
- AI responds with step-by-step instructions referencing actual UI
- Response includes deep-links to relevant pages
- **API unavailable:** Fallback to manual help documentation

**2. Discover Mode**
- User asks: "Find quiet study rooms near library"
- System extracts keywords using AI
- Queries database (Resource table with ILIKE matching)
- Applies intelligent filters:
  - Capacity inference (quiet → capacity ≤ 4)
  - Synonym mapping (library → "Library", "Information Commons")
- Returns top 6 results (title, category, location, capacity, rating, description)
- AI formats results with direct links
- Sources attributed (database-grounded)
- **API unavailable:** Keyword-only fallback search

**3. Draft Mode**
- User provides prompt: "Write message asking about projector availability"
- System uses API with context (user role, related bookings, resource details)
- AI generates appropriate message draft
- Copy button for easy use
- Attribution note displayed
- User can regenerate or edit

**Safety & Rate Limiting:**
- Rate limit: 1 request per 5 seconds per user
- PII sanitization (emails/IPs removed from prompts)
- Response validation (markdown stripped for safety)
- Graceful error messages
- 30-second timeout

### UX & Metrics

#### UX Design

**Admin Dashboard:**
- Card-based layout with color-coded status indicators
- Persistent sidebar navigation
- Breadcrumb navigation for context
- Bulk actions with confirmation dialogs
- Quick filters and search bars
- Export buttons for data

**AI Assistant:**
- Three-tab interface (Help/Discover/Draft)
- Context sidebar shows user info and relevant data
- AI responses in styled cards:
  - Summary at top
  - Bullet points for clarity
  - Action buttons (links, copy)
- Discover results link directly to resource details
- Draft includes copy-to-clipboard functionality
- Safety banner with usage guidelines
- Loading spinner with timeout indicator

#### Success Metrics

**Admin Dashboard:**
- Approval actions complete < 2 min
- ≥90% pending items resolved within 24h
- 100% critical actions logged
- Log search results < 5 sec

**AI Concierge:**
- ≥25% users try AI in first month
- ≥95% discovery responses reference actual database data
- Support ticket inquiries decrease ≥40%
- User satisfaction with AI ≥4.0/5.0
- < 1% hallucination rate (non-database responses)

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Data overload | Smart filters, metric summaries, CSV export; pin important metrics |
| Access misuse | Role-based permissions; confirmation dialogs; audit all actions |
| Logging gaps | Centralized middleware; automated test coverage |
| AI hallucinations | Database-grounded responses; no markdown rendering; manual validation |
| API availability | `OPENAI_DISABLED` toggle; graceful fallback; clear error guidance |
| Privacy concerns | PII sanitization; rate limiting; logs mask sensitive data |
| Performance | Pagination on all lists; database indexing; caching for metrics |

---

## Cross-Feature Considerations

### Security

- **Authentication:** Bcrypt password hashing
- **CSRF Protection:** Flask-WTF tokens on all forms
- **Secure Headers:**
  - Content-Security-Policy (CSP)
  - X-Frame-Options: DENY
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy
- **Rate Limiting:**
  - Login: 5 requests/min
  - Write endpoints: 10 requests/min
  - AI endpoints: 1 request/5 sec
- **SQL Injection Prevention:** Parameterized queries via SQLAlchemy
- **Role-Based Authorization:** Server-side checks on all protected routes

### Validation

- Shared validation services (`validators.py`, `sanitize.py`)
- Time window validation (future dates, start < end, min duration)
- Review payload validation (rating range, comment length)
- Message content validation (non-empty, length limits, sanitization)
- File upload validation (type, size, dimensions)

### Performance

- **Database:** SQLite with Flask-Migrate (scalable to PostgreSQL)
- **Indexing:** Frequent query columns indexed
- **Pagination:** All lists paginated (default 20 items)
- **Caching:** Aggregate ratings cached and recalculated on updates
- **Lazy Loading:** Images optimized with thumbnails

### Documentation

- README with quickstart guide
- Seeded demo accounts (admin/staff/student)
- AI feature walkthroughs
- Manual test plans with Given/When/Then format
- API endpoint documentation in code

### Measurement

- Metrics tracked via audit logs and database queries
- Pytest suite with 31 tests for regression coverage
- Manual test cases (3 positive, 3 negative scenarios)
- Performance monitoring on key endpoints

---

## Implementation Notes

### Technology Stack

- **Backend:** Flask 3.0
- **Database:** SQLAlchemy ORM with Flask-Migrate
- **AI:** OpenAI API (GPT-4o-mini) with tiktoken
- **Image Processing:** Pillow
- **Testing:** Pytest with coverage reporting
- **Architecture:** MVC + DAL pattern with service layer

### Dependencies

```
Flask==3.0.0
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
bcrypt==4.1.2
openai>=1.40.0,<2.0.0
tiktoken>=0.7.0
Pillow>=10.2.0
pytest==7.4.3
```

### Development Timeline

- **Phase 1:** Messaging system (2 weeks)
- **Phase 2:** Reviews & ratings (2 weeks)
- **Phase 3:** Admin dashboard (3 weeks)
- **Phase 4:** AI concierge (3 weeks)
- **Phase 5:** Integration & testing (2 weeks)

**Total:** 12 weeks

