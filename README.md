# PortfolioHub — Portfolio Builder Platform

A full-stack portfolio builder where users sign up, build their own portfolio (with full CRUD), and share it via a unique link.

---

## Files
| File | Purpose |
|------|---------|
| `firebase.js` | Shared Firebase config (edit this first!) |
| `index.html` | Landing page — Login & Sign Up |
| `dashboard.html` | Logged-in user manages their portfolio (CRUD) |
| `portfolio.html` | Public view of any user's portfolio |
| `style.css` | Shared styles for all pages |

---

## CRUD Map
| Action | Where | What it does |
|--------|-------|-------------|
| **Create** | Dashboard → Add Project / Add Skill | Adds new document to Firestore subcollection |
| **Read** | Dashboard + Portfolio page | Fetches and displays data in real-time |
| **Update** | Dashboard → ✏️ Edit button | Updates existing Firestore document |
| **Delete** | Dashboard → 🗑 Delete button | Removes document from Firestore |
| **Update** | Dashboard → Save Profile | Updates user profile document |

---

## Firebase Database Structure
```
users (collection)
 └── {userId} (document)
       ├── name, username, email, bio, photoURL
       ├── github, linkedin, twitter
       ├── projects (subcollection)
       │     └── {projectId} → title, desc, status, link, tags
       └── skills (subcollection)
             └── {skillId} → title, level, percent
```

---

## Setup Guide

### Step 1: Create a Firebase project
1. Go to https://firebase.google.com → sign in → "Go to Console"
2. "Add project" → name it → Continue
3. Click the **</>** Web icon → register app → copy the config

### Step 2: Enable Firebase services
- **Authentication**: Firebase Console → Authentication → Get started → Email/Password → Enable
- **Firestore**: Firebase Console → Firestore Database → Create database → Start in **test mode** → pick a region

### Step 3: Paste your config
Open `firebase.js` and replace the placeholder values:
```js
const firebaseConfig = {
  apiKey: "YOUR_REAL_KEY",
  authDomain: "your-project.firebaseapp.com",
  ...
};
```

### Step 4: Upload to GitHub
1. Create a GitHub account → New repository → name it `portfolio-hub`
2. Upload all 5 files

### Step 5: Deploy with GitHub Pages
1. Repo → Settings → Pages → Source: **main branch** → Save
2. Your site will be live at: `https://YOUR_USERNAME.github.io/portfolio-hub`

### Step 6: Fix Firebase Auth domain
1. Firebase Console → Authentication → Settings → Authorized domains
2. Add: `YOUR_USERNAME.github.io`

---

## How sharing works
Each user's public portfolio is at:
```
https://YOUR_USERNAME.github.io/portfolio-hub/portfolio.html?u=theirusername
```

Users can share this link with anyone — no login needed to view.

---

## Next steps (optional upgrades)
- Add a "Browse All Portfolios" directory page
- Let users pick a portfolio color theme
- Add image uploads with Firebase Storage
- Add a contact form on each portfolio page
