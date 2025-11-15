# Product Requirements Document (PRD)
# PRD 1: Resource Discovery & Booking System

**Project:** AiDD Campus Resource Hub  
**Document Version:** 1.0  
**Last Updated:** November 2024  
**Owner:** Product Management

---

## Feature 1: Resource Discovery & Management Platform

### Context

Campus communities manage diverse resources (study rooms, equipment, labs) but lack centralized discovery and curation. Owners need tools to create rich listings; users need intuitive search and filtering.

### Problem Statement

Resource information is scattered across emails and spreadsheets. Owners struggle to maintain listings; users waste time searching without unified filtering by location, capacity, category, or availability.

### Goals

- **Comprehensive catalog** with descriptions, image galleries, metadata (category, location, capacity, policies)
- **Full CRUD** for owners (staff/admin) with image uploads and thumbnails
- **Advanced search/filtering** (keyword, category, location, capacity, date availability, sorting)
- **Status lifecycle** (draft → published → archived) with authorization
- **Aggregate ratings** and review counts

### Non-Goals

- Real-time calendar visualization
- Payment processing
- Maintenance scheduling
- Mobile app

### Users & Flows

#### Students/Staff
- Browse published resources
- Keyword search (title/description/category/location)
- Filter (category, location, capacity_min, date)
- Sort (recent/booked/rated)
- View detail pages with booking CTA

#### Owners (Staff/Admin)
- Create listings (title, description, category, location, capacity, approval requirements)
- Upload images (JPG/PNG/WebP, max 2MB)
- Manage status (draft/published/archived)
- Edit resources

#### Admins
- Full CRUD on all resources
- Manage status
- Filter by status

### Flow Summary

#### 1. Creation
Staff/admin fills form, uploads images, sets status (default: draft). System validates, generates thumbnails.

#### 2. Search
User enters keyword/applies filters. System queries with ILIKE matching, applies filters, sorts. Cards show thumbnail, title, category, location, capacity, rating.

#### 3. Detail
Image gallery, description, category, location, capacity, approval indicator, rating/review count, "Book Now" CTA. Owner/admin see "Edit" if authorized.

#### 4. Status
- **Draft** - Owner/admin only
- **Published** - Visible to all
- **Archived** - Hidden, preserved

### UX & Metrics

#### UX Design
- Landing page features top-rated resources (limit 4) with category filters
- Card-based list with hover effects, capacity tags
- Detail view: image carousel, policy reminders, booking button
- Search bar with real-time filtering; persistent filter sidebar
- Empty states with helpful messages

#### Success Metrics
- Discovery efficiency < 2 min
- ≥80% resources have images
- ≥60% views from search/filter
- ≥90% proper status transitions
- ≥70% staff create listing in first term

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Image quality | 2MB limit, format validation, auto-thumbnails |
| Stale listings | Archive workflow prompts quarterly review |
| Search performance | Index columns, paginate results |
| Authorization | Server-side validation, role checks on write endpoints |

---

## Feature 2: Booking & Scheduling System

### Context

Resource booking requires coordination between requesters, owners, and administrators. Manual processes cause double-bookings and unclear status.

### Problem Statement

Users submit requests without knowing availability, causing conflicts. Owners receive ad hoc requests, making approval tracking difficult. Administrators lack visibility into patterns and SLAs.

### Goals

- **Prevent double-bookings** via automated conflict detection (strict overlap)
- **Flexible approval workflows** (auto-approve for open, manual for restricted)
- **Status lifecycle** (pending → approved/rejected → completed/cancelled)
- **Real-time status updates**
- **User booking views** (upcoming, past, by status)
- **Time window validation** (start < end, minimum duration, future dates)

### Non-Goals

- Calendar UI
- Recurring bookings
- Waitlists
- External calendar integration

### Users & Flows

#### Students/Staff
- Click "Book Now," select start/end datetime, submit (validated for conflicts/time windows)
- Receive feedback (auto-approved or pending)
- View booking list (sorted by start)
- See detail with status/resource/messages
- Cancel if allowed

#### Owners (Staff/Admin)
- Receive notifications for approval-required bookings
- View requests in dashboard
- Approve/reject with conflict recheck
- See all bookings for owned resources
- Complete bookings (enables reviews)

#### Admins
- Full visibility
- Approve/reject any booking
- View pending queue with SLA indicators

### Flow Summary

#### 1. Request
User enters start_dt/end_dt (future, start < end, min 1 hour). System validates, checks conflicts (queries approved/pending for overlaps).

- **Conflict:** Error with details
- **No conflict:** Booking created (status based on resource.requires_approval)
  - `False` = APPROVED
  - `True` = PENDING
- Notification sent

#### 2. Approval
Owner/admin views pending, sees context, clicks Approve/Reject. System rechecks conflicts before approval.

- **Conflict:** Error, remains pending
- **No conflict:** Status updated, notification sent, audit log created

#### 3. Transitions
Valid state transitions:
- `PENDING` → `APPROVED` (owner/admin, conflict recheck)
- `PENDING` → `REJECTED`
- `PENDING/APPROVED` → `CANCELLED`
- `APPROVED` → `COMPLETED` (enables reviews)

Invalid transitions blocked.

#### 4. Conflict Detection
**Strict overlap formula:**
```
(start_dt < existing.end_dt) AND (end_dt > existing.start_dt)
```

- Adjacent bookings (end == start) don't conflict
- Checks APPROVED/PENDING only
- Runs at creation and before approval

### UX & Metrics

#### UX Design
- Booking form shows policy reminders
- Success messages indicate status
- Status badges:
  - **Pending** - Orange
  - **Approved** - Green
  - **Completed** - Blue
  - **Cancelled** - Gray
- Detail shows timeline/schedule
- Conflict errors show specific details
- Empty states with CTAs

#### Success Metrics
- Conflicts drop ≥95% vs manual
- ≥80% pending decisions within 24h
- ≥50% auto-approved
- ≥60% marked completed
- Booking creation < 3 min

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Race conditions | Conflict recheck before approval; database transactions |
| Invalid times | Server-side validation |
| Status confusion | Clear badges/messages |
| Approval delays | Dashboard highlights pending > 24h |
| Data integrity | DAL abstraction; unit tests validate edge cases |

---

## Implementation Notes

### Technology Stack
- **Backend:** Flask + SQLAlchemy
- **Database:** SQLite (scalable to PostgreSQL)
- **Authentication:** Flask-Login with bcrypt
- **File Uploads:** Pillow for image processing
- **Architecture:** MVC + DAL pattern

### Security Considerations
- Server-side validation for all inputs
- CSRF protection on forms
- Role-based authorization checks
- Parameterized queries (SQL injection prevention)
- File upload validation (type, size, sanitization)

### Testing Coverage
- Unit tests for booking conflicts
- Unit tests for status transitions
- Integration tests for booking workflow
- Security tests for authorization
- Manual test cases for user flows

