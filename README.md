# TruthLens – AI-Assisted Claim Verification Chrome Extension

> Verify viral claims using trusted sources, not just AI opinions.

![TruthLens Banner](assets/banner.png)

---

## Overview

TruthLens is a Chrome Extension that helps users investigate claims shared on social media. Instead of relying solely on an AI model, TruthLens retrieves evidence from trusted sources, evaluates source credibility, and generates a structured verification report.

The current MVP focuses on **X (Twitter)** and demonstrates a scalable architecture that can later support additional platforms such as Reddit, Instagram, Facebook, YouTube, and news websites.

---

## Features

* Chrome Extension (Manifest V3)
* FastAPI backend
* One-click verification on X (Twitter)
* Evidence retrieval using Tavily Search API
* AI-assisted reasoning with Gemini
* Source Trust Layer (Tier 1–Tier 4 credibility)
* Redis caching for faster repeated requests
* Supabase authentication and verification history
* Modular provider architecture
* Platform adapter architecture
* Modern Side Panel UI

---

## Tech Stack

### Frontend

* Chrome Extension (Manifest V3)
* JavaScript
* HTML
* CSS

### Backend

* FastAPI
* Python
* Redis
* Supabase
* Tavily Search API
* Gemini API

---

## Architecture

```text
Chrome Extension
        │
        ▼
FastAPI Backend
        │
        ▼
Verification Orchestrator
        │
 ┌──────┴────────┐
 │               │
 ▼               ▼
Redis        Supabase
 │               │
 ▼               ▼
Cache       History/Auth
        │
        ▼
Evidence Retrieval (Tavily)
        │
        ▼
Source Trust Layer
        │
        ▼
Gemini AI
        │
        ▼
Verification Report
```

---

## Verification Pipeline

1. User clicks the TruthLens button.
2. The extension extracts the claim.
3. The backend generates a search query.
4. Tavily retrieves relevant sources.
5. The Source Trust Layer evaluates source credibility.
6. Gemini summarizes only the retrieved evidence.
7. The verification report is returned to the extension.

---

## Project Structure

```text
TruthLens/
│
├── extension/
│   ├── adapters/
│   ├── onboarding/
│   ├── sidepanel/
│   ├── assets/
│   ├── background.js
│   ├── content.js
│   └── manifest.json
│
└── backend/
    ├── api/
    ├── providers/
    ├── engines/
    ├── trust/
    ├── database/
    ├── cache/
    ├── core/
    └── main.py
```

---

## Current Status

### Completed

* X (Twitter) integration
* Chrome Extension
* FastAPI backend
* Verification API
* Redis caching
* Supabase integration
* Source Trust Layer
* Verification history
* Modular architecture

### In Progress

* Image verification improvements
* Video verification
* Better claim extraction
* Improved evidence retrieval
* Multi-platform support

---

## Limitations

The current version is an MVP focused on demonstrating the architecture.

* Verification quality depends on available public sources.
* Image verification is experimental.
* Video verification is under development.
* Some breaking news may not yet have sufficient reliable evidence.

TruthLens should be used as a tool to assist investigation rather than as the sole authority on factual claims.

---

## Installation

### Backend

```bash
git clone https://github.com/yourusername/truthlens.git

cd backend

pip install -r requirements.txt

python -m backend.main
```

### Extension

1. Open Chrome.
2. Navigate to `chrome://extensions`.
3. Enable **Developer Mode**.
4. Click **Load unpacked**.
5. Select the `extension/` folder.

---

## Environment Variables

```env
GEMINI_API_KEY=

TAVILY_API_KEY=

SUPABASE_URL=

SUPABASE_ANON_KEY=

SUPABASE_SERVICE_KEY=

REDIS_URL=
```

---

## Future Roadmap

### Version 1.1

* Better evidence retrieval
* Improved prompt grounding
* OCR improvements

### Version 1.2

* Image verification
* Reverse image search

### Version 1.3

* Video verification
* Speech-to-text pipeline

### Version 2.0

* Reddit
* Instagram
* Facebook
* YouTube
* News websites
* Mobile applications

---

## License

MIT License

---

## Author

**Divya Mohan Nayak**

Final Year B.Tech Student

Interested in AI, Browser Extensions, Backend Engineering, and Large-Scale Software Systems.

---

⭐ If you find this project interesting, feel free to star the repository and share feedback.

