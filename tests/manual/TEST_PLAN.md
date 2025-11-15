# Manual Test Plan — Campus Resource Hub

**Purpose**: Validate key user flows and edge cases that require manual verification.

**Test Environment**: Local development server (Flask app running on `http://127.0.0.1:5000`)

---

## Test Cases

| Test ID | Scenario (Given / When / Then) | Step-by-Step Actions | Expected Result | Status | Notes |
|---------|--------------------------------|----------------------|-----------------|--------|-------|
| **M-01** | **POSITIVE**: Student books available resource | **Given** a logged-in student user and a published resource with no conflicts<br>**When** the student selects a valid date/time and submits booking<br>**Then** booking is created with PENDING or APPROVED status | 1. Login as `student@demo.edu` / `Student123!`<br>2. Navigate to `/resources`<br>3. Click on "Conference Room A"<br>4. Select tomorrow's date, 10:00-12:00<br>5. Click "Book Now"<br>6. Verify success message appears<br>7. Navigate to "My Bookings"<br>8. Confirm booking appears in list | Success message: "Booking request submitted"<br>Booking appears in "My Bookings" with correct date/time<br>Status: PENDING or APPROVED | ☐ Pass<br>☐ Fail | |
| **M-02** | **POSITIVE**: Admin approves pending booking | **Given** a pending booking exists<br>**When** admin navigates to Admin Dashboard and clicks "Approve"<br>**Then** booking status changes to APPROVED and user is notified | 1. Login as `admin@demo.edu` / `Admin123!`<br>2. Navigate to `/admin`<br>3. Click "Bookings" tab<br>4. Locate pending booking<br>5. Click "Approve" button<br>6. Logout and login as the student who made the booking<br>7. Check "My Bookings" page | Booking status changes to "Approved"<br>Flash message: "Booking approved"<br>Student sees APPROVED status in their bookings list | ☐ Pass<br>☐ Fail | |
| **M-03** | **POSITIVE**: User leaves review after completed booking | **Given** a completed booking (status = COMPLETED)<br>**When** user navigates to the resource detail page and submits a review<br>**Then** review is saved and displayed | 1. Login as student with completed booking<br>2. Navigate to the booked resource detail page<br>3. Scroll to "Reviews" section<br>4. Enter rating (4 stars) and comment "Great room!"<br>5. Click "Submit Review"<br>6. Refresh page | Review appears in the reviews list<br>Resource average rating updates<br>Flash message: "Review submitted" | ☐ Pass<br>☐ Fail | |
| **M-04** | **NEGATIVE**: User attempts to book with end time before start time | **Given** a logged-in student on resource detail page<br>**When** user enters end time before start time and submits<br>**Then** form validation error is displayed | 1. Login as `student@demo.edu` / `Student123!`<br>2. Navigate to any published resource<br>3. Enter start time: "2025-11-15 14:00"<br>4. Enter end time: "2025-11-15 12:00" (before start)<br>5. Click "Book Now" | Error message: "End time must be after start time"<br>Booking is NOT created<br>Form stays on page with error displayed | ☐ Pass<br>☐ Fail | |
| **M-05** | **NEGATIVE**: Student attempts to access Admin Dashboard | **Given** a logged-in student user<br>**When** student navigates to `/admin`<br>**Then** access is denied (403 Forbidden or redirect to home) | 1. Login as `student@demo.edu` / `Student123!`<br>2. Manually type `/admin` in address bar<br>3. Press Enter | 403 Forbidden page OR redirect to home page<br>Flash message: "Access denied" or "Admin privileges required" | ☐ Pass<br>☐ Fail | |
| **M-06** | **NEGATIVE**: User attempts SQL injection in search field | **Given** user on resources search page<br>**When** user enters SQL injection string in search box<br>**Then** search is handled safely with no database error | 1. Navigate to `/resources`<br>2. Enter in search box: `'; DROP TABLE resources; --`<br>3. Click "Search" | Search returns 0 results (or matches literal string)<br>NO database error<br>NO data loss<br>Application remains functional | ☐ Pass<br>☐ Fail | Verify database integrity after test |

---

## Testing Notes

- **Preconditions**: Database must be seeded with test users, resources, and bookings using `flask --app src.app seed`
- **Test Users**:
  - Student: `student@demo.edu` / `Student123!`
  - Admin: `admin@demo.edu` / `Admin123!`
  - Staff: `staff@demo.edu` / `Staff123!`
- **Environment**: All tests performed on local Flask dev server
- **Browser**: Chrome 120+ or Firefox 115+ (latest stable)

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester | | | |
| Reviewer | | | |

---

*This manual test plan complies with the AiDD Final Project Testing requirements: 6 test cases (3 positive, 3 negative) with Given/When/Then format.*

