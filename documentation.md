Project: 100 Days of ___ — Social Media App

Overview
--------
This repository contains a full-stack social media application with a Django REST API backend and a React frontend. The app models "threads" (100-day challenges / projects) and supports posts tied to threads, user participation in threads, likes, comments, following/friend relationships, and discovery features.

Key Features
------------
- User management
  - Sign up, login (JWT via SimpleJWT), profile edit
  - Friend/follow system with friend requests, accept/decline, cancel
  - User profile pages showing their threads and posts

- Threads (100-day challenges / projects)
  - Create/join/leave threads
  - Track current day per user in a thread (UserThread)
  - Thread discovery and suggestions
  - View thread detail with posts, optionally filtered by a specific user

- Posts
  - Create posts tied to a user's participation in a thread (user_thread)
  - Like/unlike posts
  - Comment on posts
  - Attachments (images/files) support (PostAttachment model)

- Social features
  - Friend suggestions (mutual friends, common threads)
  Project: 100 Days of ___ — Social Media App

  Overview
  --------
  This repository contains a full-stack social media application built for short-form, daily challenge-style content ("100-day" threads). It pairs a Django REST API backend with a React + Tailwind frontend. Users can join threads (projects), post daily updates, follow other users, send friend requests, and discover active threads and people.

  This document is written for a human reader: developers, testers and product people who want an overview of what the app does, how to use the API, and how to run it locally.

  Quick tour (what a user experiences)
  ----------------------------------
  - Sign up and sign in using email/password. Authentication uses JWT (SimpleJWT).
  - Join or create a "thread" (a 100-day challenge such as "100 days of coding").
  - Each thread shows a timeline of posts from users who joined it. When viewing a user's profile you can click a thread to see only that user's posts in the thread (sorted by day).
  - Create posts tied to your participation in a thread (optionally attaching images).
  - Like and comment on posts.
  - Discover active threads and people to follow; the app suggests friends based on mutual friends and shared threads.

  Key Features (human descriptions)
  ---------------------------------
  - User accounts & profiles: editable profiles, avatar support, and account management.
  - Friend system: send, cancel, accept or decline friend requests. Friends appear in activity feeds.
  - Threads: start a new thread or join an existing one. Each user has a per-thread progress (current day) so the UI can show a "thread card" with progress.
  - Posts: posts belong to a user's participation in a thread (a post links to a UserThread). Posts support text, optional attachments, likes and comments.
  - Discovery & sidebars: left/right sidebars surface recently active threads, recent friend activity, and suggested threads/people to follow.

  API Reference (practical, with examples)
  ---------------------------------------
  Base URL: http://localhost:8000/api/

  Authentication
  --------------
  Use JWT access tokens for protected endpoints. Example header:

  Authorization: Bearer <ACCESS_TOKEN>

  Account endpoints
  -----------------
  - GET /api/me/
    - Returns the currently authenticated user's data.

  - POST /api/login/  (SimpleJWT token endpoint)
    - Obtain access and refresh tokens.

  - POST /api/signup/
    - Create a new user account.

  - GET /api/posts/profile/<user_id>/
    - Returns profile info and the list of threads that user has joined.

  - POST /api/account/friends/<uuid:pk>/request/
    - Send a friend request to a user (pk = their id).

  - POST /api/account/friends/<uuid:pk>/cancel/
    - Cancel a previously sent request.

  - GET /api/account/recent-friends/
    - Returns friends who posted within the last 7 days (used by the left sidebar).

  - GET /api/account/suggested-friends/
    - Returns suggested people to follow, prioritized by mutual friends and shared threads.

  Posts endpoints
  ---------------
  - GET /api/posts/
    - Personalized feed for the logged-in user (paginated). Example: /api/posts/?page=1&limit=10

  - GET /api/posts/public/
    - Public feed of all posts.

  - POST /api/posts/create/
    - Create a new post. Required payload (example):

    {
      "user_thread_id": "<user_thread_uuid>",
      "body": "Day 5: shipped a feature",
      "attachments": []
    }

    - Server response: created post object (201).

  - POST /api/posts/<post_id>/like/
    - Like/unlike a post (toggles depending on user state).

  - DELETE /api/posts/<post_id>/delete/
    - Delete a post you own.

  - POST /api/posts/<post_id>/comment/
    - Add a comment to a post. Body: { "body": "Nice job!" }

  Thread endpoints
  ----------------
  - GET /api/posts/threads/
    - List available threads (topics/projects).

  - POST /api/posts/threads/create/
    - Create a thread. Payload example: { "topic": "100 Days of Rust", "description": "Daily Rust exercises" }

  - POST /api/posts/threads/join/
    - Join a thread: { "thread_id": "<thread_uuid>" }

  - GET /api/posts/threads/my/
    - Returns threads the current user has joined.

  - GET /api/posts/threads/<thread_id>/?user_id=<user_id>
    - Get thread details and posts. If user_id is provided, returns only that user's posts within the thread and sorts posts by day_number then created_at.

  - GET /api/posts/recent-threads/
    - Returns threads with activity in the last 7 days (for the left sidebar).

  - GET /api/posts/suggested-threads/
    - Suggested threads for the user (threads they have not joined, ordered by activity/participants).

  Data shapes (examples)
  ----------------------
  Post object (example):

  {
    "id": "uuid",
    "body": "Day 3: learned X",
    "created_by": { "id": "uuid", "name": "Alice" },
    "user_thread": "uuid",
    "day_number": 3,
    "likes_count": 4,
    "comments_count": 2,
    "attachments": []
  }

  Thread object (example):

  {
    "id": "uuid",
    "topic": "100 Days of Coding",
    "description": "Daily coding challenges",
    "participants_count": 24,
    "posts_count": 120
  }

  Frontend notes
  --------------
  - Project structure: `100Daysof___/src` contains React sources.
  - Styling uses Tailwind CSS. Components are split into UI, threads, posts, profile, and sidebars.
  - Key component behavior:
    - `MainPage.jsx` provides a responsive three-column layout. On small screens columns stack.
    - `ThreadDetailPage.jsx` reads the optional `user_id` query parameter and calls the thread detail API with it to show a user's posts in that thread.
    - Sidebar components call their respective endpoints; these endpoints require authentication.

  Running locally (developer quick start)
  ------------------------------------
  Backend (Django)

  1. From the `100_days_of__api` folder, activate the virtual environment and run the server:

  ```bash
  cd 100_days_of__api
  source .venv/bin/activate
  python manage.py runserver
  ```

  2. The API will be available at http://127.0.0.1:8000/api/

  Frontend (React)

  1. From the `100Daysof___` folder:

  ```bash
  cd 100Daysof___
  npm install
  npm start
  ```

  2. The frontend will typically run at http://localhost:3000

  Quick curl examples
  -------------------
  - Get authenticated user (replace token):

  ```bash
  curl -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:8000/api/me/
  ```

  - Create a post (replace thread id and token):

  ```bash
  curl -X POST http://127.0.0.1:8000/api/posts/create/ \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"user_thread_id":"<UUID>", "body":"Day 1: wrote tests"}'
  ```

  Developer guidance & next steps
  ------------------------------
  - Tests: add Django unit tests for endpoint behaviour (especially thread filtering, friend suggestions, and post creation).
  - Performance: sidebar queries (recent threads, suggested friends) use aggregates and may need indexing or caching when the dataset grows.
  - UX: add graceful fallbacks for missing avatars and empty sidebars, and enable optimistic UI updates for likes and friend requests.

  Known details & gotchas
  ----------------------
  - Many endpoints require a valid JWT access token. If calls return 401, check the Authorization header and token expiry.
  - Thread posts are sorted by day_number first, then created_at — this ensures daily progression ordering.
  - When viewing a user's profile and clicking a thread card, the frontend passes `?user_id=<id>` to the thread detail endpoint to filter posts to that user's contributions only.

  Contact
  -------
  Repository owner: md-tonmoy007

  Generated on: 2025-09-16
