Leetle Frontend (Demo)

This folder contains a demo frontend built with Vite + React + Tailwind CSS. It is intentionally self-contained and uses a static mock API and browser localStorage so you can demo the UI without a backend.

Quick start (PowerShell):

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (usually http://localhost:5173) and navigate the Home, Problem, and Leaderboard pages. Submit a demo solution on the Problem page to populate the leaderboard (stored in localStorage).

Notes:
- Tech stack follows the project artifacts (React + Tailwind).
- No backend is required for the demo; submissions are simulated and saved to localStorage.
- To integrate with the Flask backend later, replace the mock fetches with actual API endpoints.
