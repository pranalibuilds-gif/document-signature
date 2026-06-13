# Release Candidate (RC-1) Master Checklist

This is the official product sign-off checklist. Every checkbox must be manually verified.

---

# 0. PROJECT SIGN-OFF

## Product Identity

* [ ] Product name finalized
* [ ] Logo finalized
* [ ] Favicon added
* [ ] Browser tab title correct
* [ ] Metadata configured
* [ ] OpenGraph metadata configured
* [ ] App version visible somewhere

---

# 1. AUTHENTICATION

## Registration

* [ ] Register valid user
* [ ] Duplicate email blocked
* [ ] Invalid email blocked
* [ ] Weak password blocked
* [ ] Error messages readable
* [ ] Loading state visible
* [ ] Success flow clear

## Email Verification

* [ ] Verification email received
* [ ] Link works
* [ ] Expired link handled
* [ ] Already verified handled
* [ ] Resend works
* [ ] Verification banner visible
* [ ] Banner disappears after verification

## Login

* [ ] Login succeeds
* [ ] Invalid credentials handled
* [ ] Loading state visible
* [ ] Refresh survives reload
* [ ] Logout works
* [ ] Session restored after refresh

## Session Expiry

* [ ] 401 interceptor works
* [ ] User redirected
* [ ] Auth store cleared
* [ ] Friendly message displayed

---

# 2. DASHBOARD

## Metrics

* [ ] Documents count correct
* [ ] Pending count correct
* [ ] Completed count correct
* [ ] Needs attention count correct

## States

* [ ] Loading state
* [ ] Empty state
* [ ] Error state

## Activity

* [ ] Recent activity accurate
* [ ] Links work

---

# 3. DOCUMENTS LIST

## Listing

* [ ] Documents load
* [ ] Search works
* [ ] Filter works
* [ ] Sorting works

## States

* [ ] Empty state
* [ ] No results state
* [ ] Loading state
* [ ] Error state

## Visibility

* [ ] Status badges accurate
* [ ] Dates accurate
* [ ] Ownership correct

---

# 4. DOCUMENT CREATION

## Create

* [ ] Create document
* [ ] Required validation
* [ ] Optional description works
* [ ] Redirect after create

## Edge Cases

* [ ] Empty name blocked
* [ ] Very long name handled
* [ ] Special characters handled

---

# 5. PDF UPLOAD

## Upload

* [ ] Drag and drop works
* [ ] File picker works
* [ ] PDF preview works

## Validation

* [ ] Non-PDF blocked
* [ ] Large file blocked
* [ ] Corrupt PDF handled

## UX

* [ ] Upload progress visible
* [ ] Success feedback visible

---

# 6. SIGNERS

## Add

* [ ] Add signer
* [ ] Multiple signers
* [ ] Max signer limit enforced

## Validation

* [ ] Invalid email blocked
* [ ] Duplicate email blocked

## Removal

* [ ] Remove signer
* [ ] UI updates correctly

---

# 7. PDF EDITOR

## Rendering

* [ ] PDF loads
* [ ] Multiple pages render
* [ ] Zoom works
* [ ] Resize works

## Field Placement

### Signature

* [ ] Place field
* [ ] Move field
* [ ] Delete field

### Text

* [ ] Place field
* [ ] Move field
* [ ] Delete field

### Date

* [ ] Place field
* [ ] Move field
* [ ] Delete field

## Assignment

* [ ] Assign signer
* [ ] Reassign signer

## Persistence

* [ ] Save progress
* [ ] Reload preserves fields

## Safety

* [ ] Unsaved changes warning
* [ ] Browser refresh warning

---

# 8. DOCUMENT ACTIVATION

## Validation

* [ ] Missing PDF blocked
* [ ] Missing signer blocked
* [ ] Missing fields blocked

## Activation

* [ ] DRAFT → PENDING
* [ ] UI updates instantly
* [ ] Email sent

---

# 9. EMAILS

## Invitation

* [ ] Email arrives
* [ ] Branding correct
* [ ] Link correct

## Completion

* [ ] Completion email arrives

## Rejection

* [ ] Rejection email arrives

## Verification

* [ ] Verification email arrives

---

# 10. SIGNING EXPERIENCE

## Entry

* [ ] Valid token works
* [ ] Invalid token handled
* [ ] Expired token handled

## Viewer

* [ ] PDF visible
* [ ] Assigned fields visible
* [ ] Other fields hidden

## Progress

* [ ] Progress bar accurate
* [ ] Required count accurate

## Next Required Field

* [ ] Button works
* [ ] Scroll works

---

# 11. SIGNATURE MODAL

## Input

* [ ] Name validation
* [ ] Empty blocked

## Fonts

* [ ] Every font renders
* [ ] Preview works

## Save

* [ ] Apply works
* [ ] Cancel works

---

# 12. TEXT FIELDS

* [ ] Open modal
* [ ] Save value
* [ ] Edit value

---

# 13. DATE FIELDS

* [ ] Auto-fill works
* [ ] Date format correct

---

# 14. SIGNING SUBMISSION

## Validation

* [ ] Missing required fields blocked

## Success

* [ ] Submit works
* [ ] Status updates

## Duplicate Submission

* [ ] Prevented

---

# 15. REJECTION FLOW

## UI

* [ ] Reject button visible
* [ ] Reason required

## Backend

* [ ] Status becomes REJECTED
* [ ] Notifications sent

---

# 16. COMPLETION ENGINE

* [ ] Partial signing works
* [ ] Final signer completes
* [ ] Status becomes COMPLETED

---

# 17. FINAL PDF

## Generation

* [ ] PDF generated

## Accuracy

* [ ] Signature visible
* [ ] Text fields visible
* [ ] Dates visible

## Download

* [ ] Download works

---

# 18. OWNER COMPLETION VIEW

* [ ] Final PDF discoverable
* [ ] Signer statuses visible
* [ ] Activity visible

---

# 19. AUDIT TRAIL

Verify:

* [ ] Registration
* [ ] Login
* [ ] Upload
* [ ] Signer add
* [ ] Field add
* [ ] Activation
* [ ] Signing
* [ ] Completion
* [ ] Rejection

---

# 20. EXPIRATION

* [ ] Expired document transitions
* [ ] Expired token blocked
* [ ] Owner informed

---

# 21. RESPONSIVE TESTING

## Mobile

* [ ] 375px
* [ ] 390px
* [ ] 430px

## Tablet

* [ ] 768px
* [ ] 1024px

## Desktop

* [ ] 1440px

---

# 22. ACCESSIBILITY

* [ ] Keyboard navigation
* [ ] Focus states
* [ ] Labels
* [ ] Contrast
* [ ] Screen-reader basics

---

# 23. PERFORMANCE

## Frontend

* [ ] No console errors
* [ ] No React warnings

## Backend

* [ ] No startup errors
* [ ] No unhandled exceptions

---

# 24. SECURITY

* [ ] Unauthorized access blocked
* [ ] IDOR attempts blocked
* [ ] Tokens hashed
* [ ] Refresh rotation works
* [ ] Rate limiting works
* [ ] Admin routes protected

---

# 25. DEPLOYMENT READINESS

## Backend

* [ ] Production env file
* [ ] Production DB
* [ ] Production email provider

## Frontend

* [ ] Production build succeeds

## Docker

* [ ] Build succeeds
* [ ] Compose succeeds

## CI

* [ ] Backend CI green
* [ ] Security CI green

---

# FINAL RELEASE GATE

Do not deploy until all are true:

```text
□ Happy Path Passed
□ Multi-Signer Passed
□ Rejection Passed
□ Expiration Passed
□ Mobile Passed
□ Security Passed
□ Final PDF Passed
□ No Critical Bugs
□ No Major Friction
□ Recruiter Demo Passed
```
