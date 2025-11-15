# Demo Script: Campus Resource Hub
**7-Minute Live Demonstration**

> **Design Note**: As you navigate, notice the modern Airbnb-inspired interface with Indiana University's cream and crimson colors, card-based layouts, and responsive design.

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@demo.edu` | `Admin123!` |
| **Staff** | `staff@demo.edu` | `Staff123!` |
| **Student** | `student@demo.edu` | `Student123!` |

---

## Script Flow

### 1. Student Search & Booking (1 min)

**[Navigate to home page]**

> "Let me show you Campus Resource Hub—a full-stack application for discovering and booking shared university resources. I'll start by logging in as a student."

**[Log in as Student: `student@demo.edu` / `Student123!`]**

> "First, students need to find resources. Let's say I'm looking for a quiet place to study."

**[Click 'Resources' → Type 'quiet study room' in search bar]**

> "The search uses natural language processing to interpret queries. Here are the results—notice the card layout with images, location, capacity, and ratings."

**[Click 'View Details' on a result]**

> "On the detail page, you see the full description, image gallery, booking policies, and reviews. Now let's book it."

**[Fill booking form: Tomorrow 10:00 AM to 12:00 PM → Click 'Request Booking']**

> "I select my time slot, submit, and... there it is—'Pending' status. This resource requires approval, so it goes into a queue for staff review."

**Key Points:**
- ✅ Natural language search
- ✅ Date validation
- ✅ Approval workflow triggered

---

### 2. Admin Approval with Messaging (1.5 min)

**[Log out → Log in as Admin: `admin@demo.edu` / `Admin123!`]**

> "Now I'm an administrator. Notice the red admin banner—role-based access control ensures only authorized users see this."

**[Click 'Admin Dashboard']**

> "The dashboard shows pending approvals at a glance. Here's the student's booking request."

**[View pending booking → Click message button to expand]**

> "Before approving, I can review any messages from the requester. The messaging is threaded and contextual—I can see the full conversation right here inline without leaving the page."

**[Optionally type a quick reply: 'Looks good!' → Send]**

> "I can reply directly if needed. Now, I'll approve this request."

**[Click 'Approve' button]**

> "Approved! The student will see the status change immediately. This action is also logged in the audit trail with my user ID, timestamp, and IP address for compliance."

**Key Points:**
- ✅ Admin-only access
- ✅ Inline messaging during approval
- ✅ Audit trail logged
- ✅ Status update in real-time

---

### 3. Messaging Exchange (1 min)

**[Log out → Log in as Student]**

> "Back as the student, let me check my conversations."

**[Click 'My Conversations' in navbar]**

> "This is the messaging hub—all booking conversations in one place. You can see previews, status badges, and message counts. Notice the modern UI."

**[Click 'Open Conversation' on the approved booking]**

> "Here's the thread. See the color-coded participant badges—blue for requester, yellow for owner. Messages are styled like a chat interface with bubbles aligned by sender."

**[Type message: 'Thank you for approving! I'll be there on time.' → Send]**

> "Messages are threaded per booking, not real-time chat, but they keep everything organized. Let me show the owner's perspective."

**[Log out → Log in as Staff: `staff@demo.edu`]**

**[Navigate to 'My Conversations' → Open same thread]**

> "As the resource owner, I can reply to the student."

**[Type: 'You're welcome! The room is ready.' → Send]**

> "Perfect. Only participants—requester, owner, and admins—can access each thread. Authorization is enforced server-side."

**Key Points:**
- ✅ Chat-style messaging UI
- ✅ Role badges and color coding
- ✅ Conversation overview page
- ✅ Authorization enforcement

---

### 4. Review Submission (1 min)

**[Log in as Admin → Navigate to the booking → Click 'Mark Completed']**

> "After a booking ends, admins mark it completed. This enables the review feature."

**[Log out → Log in as Student → Navigate to resource detail page]**

> "Now the student can leave feedback. Let me click the 'Reviews' tab."

**[Scroll to review form]**

> "Review forms only appear if you've completed a booking—eligibility is enforced. Let me submit one."

**[Fill: 5 stars + 'Excellent study space! Very quiet and well-maintained.' → Submit]**

> "Submitted! The rating average updates automatically, and the review appears in the list. This helps future users make informed decisions."

**Key Points:**
- ✅ Eligibility-based (completed bookings only)
- ✅ One review per user per resource
- ✅ Aggregate rating calculation

---

### 5. Sorting & Filtering (30 sec)

**[Navigate to 'Resources' page]**

> "Let's talk about discovery. Users can sort resources by multiple criteria."

**[Select 'Top Rated' from dropdown]**

> "Top Rated shows highest-rated resources first. We also have 'Most Booked' for popular items, and 'Recent' for new additions."

**[Show date filter]**

> "Date filtering shows only resources available on specific days—conflict detection runs in the background to exclude booked slots."

**Key Points:**
- ✅ Multiple sort options
- ✅ Date-based availability filtering
- ✅ Performance-optimized with denormalized fields

---

### 6. AI Concierge (2 min)

**[Click 'AI Concierge' in navbar]**

> "This is the advanced feature—an AI-powered assistant with three modes. Let's start with Help."

**[Select 'Help / How-to' → Type: 'How do I make a booking?' → Submit]**

> "The AI explains the booking process step-by-step with references to actual UI elements. This reduces support burden."

**[Switch to 'Discover Resources' mode → Type: 'Find 3D printer near lab' → Submit]**

> "Now Discover mode. I'm using natural language—'3D printer near lab.' The AI extracts keywords, queries the database with intelligent matching, and returns actual resources."

**[Show results with links]**

> "Notice these are real resource IDs—no hallucinations. The AI uses RAG-lite: retrieval-augmented generation grounded in our database. I can click any link to navigate directly."

**[Optionally show Draft mode briefly]**

> "Draft mode helps users compose polite messages. For example, asking about equipment availability."

**Key Points:**
- ✅ Three modes: Help, Discover, Draft
- ✅ Natural language processing
- ✅ Database-grounded (no hallucinations)
- ✅ Graceful fallback if API unavailable

---

### 7. All Bookings View (1 min)

**[Log in as Admin → Navigate to 'All Bookings' in sidebar]**

> "Admins need visibility into all bookings, not just pending approvals. This view shows everything—pending, approved, completed, cancelled."

**[Click message button on any booking]**

> "And here's the key: admins can view and reply to messages for ANY booking, even ones that were auto-approved. This is critical for resources that don't require approval but still need communication."

**[Expand a thread, optionally reply]**

> "Comprehensive oversight—this ensures nothing falls through the cracks."

**Key Points:**
- ✅ Complete booking history
- ✅ Inline messaging for all bookings
- ✅ Essential for auto-approved resources

---

### 8. Admin Logs & Security (1 min)

**[Click 'Audit Logs' in sidebar]**

> "Let's talk security and compliance. Every critical admin action is logged here."

**[Scroll through logs]**

> "You see booking approvals, review moderation, timestamps, and IP addresses. This creates an audit trail for investigations."

**[Mention security while staying on logs page]**

> "The application also implements enterprise-grade security:
> - **CSRF protection** on all forms
> - **Secure HTTP headers**—Content Security Policy, X-Frame-Options, Referrer Policy
> - **Rate limiting**—5 login attempts per minute, cooldowns on AI endpoints
> - **Bcrypt password hashing** with strength requirements
> - **SQL injection prevention** via parameterized queries"

**[Optional: Show browser DevTools → Network → Click any request → Headers tab]**

> "If you check DevTools, you'll see security headers on every response."

**Key Points:**
- ✅ Complete audit trail
- ✅ Security headers visible
- ✅ Rate limiting prevents abuse
- ✅ OWASP best practices

---

## Closing (15 sec)

**[Navigate back to home page]**

> "To summarize: Campus Resource Hub combines AI-powered discovery with secure, role-based workflows. Students find and book resources naturally, staff manage approvals efficiently, and admins have complete oversight with audit trails. The AI concierge enhances UX, and security is built-in from the ground up."

> "The tech stack is Flask, SQLAlchemy, OpenAI API, with MVC+DAL architecture. All code is tested—31 automated tests, 100% pass rate, full security coverage."

> "Thank you!"

---

## Demo Tips

### Before You Start
- ✅ Run `python src/app.py` to start server
- ✅ Verify seed data exists (admin/staff/student accounts)
- ✅ Have demo credentials visible
- ✅ Clear browser cookies if testing multiple roles
- ✅ Check OpenAI API key if demonstrating AI features

### During Demo
- **Pace yourself**: 7 minutes is tight—prioritize core features
- **Skip if needed**: AI Concierge can be shortened if running long
- **Show, don't tell**: Click through UI rather than explaining theory
- **Highlight visuals**: Point out IU branding, card layouts, status badges

### If Things Go Wrong
- **Database empty**: Run `flask --app src.app seed`
- **OpenAI errors**: Set `OPENAI_DISABLED=1` in `.env` and show keyword fallback
- **Login fails**: Check credentials, verify seed command ran
- **Port conflict**: Change port in `src/app.py` (line 463) or kill existing process

---

## Time Breakdown

| Section | Time | Priority |
|---------|------|----------|
| Student Search & Booking | 1 min | **High** |
| Admin Approval & Messaging | 1.5 min | **High** |
| Messaging Exchange | 1 min | Medium |
| Review Submission | 1 min | Medium |
| Sorting & Filtering | 0.5 min | Low |
| AI Concierge | 2 min | **High** (Advanced Feature) |
| All Bookings View | 1 min | Medium |
| Admin Logs & Security | 1 min | **High** |
| **Total** | **9 min** | **7 min target** |

*If running over: Skip Messaging Exchange and/or Sorting sections*

---

## Key Talking Points (Memorize These)

✅ **"Natural language search powered by OpenAI"**  
✅ **"Role-based access control—students, staff, admins"**  
✅ **"Conflict detection prevents double-bookings"**  
✅ **"Inline messaging during approval workflow"**  
✅ **"AI Concierge with RAG-lite—no hallucinations"**  
✅ **"Enterprise security—CSRF, headers, rate limiting, audit logs"**  
✅ **"MVC+DAL architecture, 31 passing tests, 100% success rate"**

---

**Built for AiDD (AI-Driven Development) X501 Capstone Project**  
**Indiana University - Kelley School of Business - Fall 2025**

