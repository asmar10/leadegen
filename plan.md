Shopify Lead Generation Tool - Implementation Plan                                                 │
     │                                                                                                    │
     │ Overview                                                                                           │
     │                                                                                                    │
     │ A web-based tool to discover and extract Shopify store data based on niche and location, with a    │
     │ filterable dashboard interface.                                                                    │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Design Principles                                                                                  │
     │                                                                                                    │
     │ KISS (Keep It Simple, Stupid)                                                                      │
     │                                                                                                    │
     │ - Start with minimal viable features, add complexity only when needed                              │
     │ - Prefer simple, readable code over clever optimizations                                           │
     │ - One function = one job, clear naming                                                             │
     │                                                                                                    │
     │ DRY (Don't Repeat Yourself)                                                                        │
     │                                                                                                    │
     │ - Shared utilities for common operations (API calls, validation, formatting)                       │
     │ - Reusable scraper base class                                                                      │
     │ - Centralized configuration and constants                                                          │
     │                                                                                                    │
     │ SOLID Principles                                                                                   │
     │                                                                                                    │
     │ - Single Responsibility: Each module/class handles one concern                                     │
     │ - Open/Closed: Scrapers extendable via base class without modification                             │
     │ - Liskov Substitution: All scrapers interchangeable via common interface                           │
     │ - Interface Segregation: Small, focused interfaces (e.g., separate scraper vs extractor)           │
     │ - Dependency Inversion: Depend on abstractions (repositories, services) not implementations        │
     │                                                                                                    │
     │ Atomic Design (Frontend)                                                                           │
     │                                                                                                    │
     │ atoms     → molecules  → organisms   → templates → pages                                           │
     │ (Button)    (SearchInput) (SearchForm)  (Layout)    (/search)                                      │
     │ - Atoms: Single UI elements (Button, Input, Badge)                                                 │
     │ - Molecules: Simple combinations of atoms (SearchInput = Input + Button)                           │
     │ - Organisms: Complex sections (SearchForm, LeadsTable, FilterPanel)                                │
     │ - Templates: Page layouts without data                                                             │
     │ - Pages: Templates with real data (Next.js routes)                                                 │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Tech Stack (Recommended)                                                                           │
     │ ┌───────────┬─────────────────┬────────────────────────────────────────────────────────────────────│
     │ ─────┐                                                                                             │
     │ │   Layer   │   Technology    │                                 Reason                             │
     │      │                                                                                             │
     │ ├───────────┼─────────────────┼────────────────────────────────────────────────────────────────────│
     │ ─────┤                                                                                             │
     │ │ Backend   │ Python +        │ Best ecosystem for web scraping (Playwright, BeautifulSoup), async │
     │      │                                                                                             │
     │ │           │ FastAPI         │ support                                                            │
     │      │                                                                                             │
     │ ├───────────┼─────────────────┼────────────────────────────────────────────────────────────────────│
     │ ─────┤                                                                                             │
     │ │ Frontend  │ Next.js (React) │ Fast dashboard development, good data table libraries              │
     │      │                                                                                             │
     │ ├───────────┼─────────────────┼────────────────────────────────────────────────────────────────────│
     │ ─────┤                                                                                             │
     │ │ Database  │ PostgreSQL      │ Reliable, good for structured lead data, full-text search          │
     │      │                                                                                             │
     │ ├───────────┼─────────────────┼────────────────────────────────────────────────────────────────────│
     │ ─────┤                                                                                             │
     │ │ Scraping  │ Playwright      │ Handles JavaScript-rendered pages (Shopify stores)                 │
     │      │                                                                                             │
     │ ├───────────┼─────────────────┼────────────────────────────────────────────────────────────────────│
     │ ─────┤                                                                                             │
     │ │ Task      │ Celery + Redis  │ Background job processing for scraping tasks                       │
     │      │                                                                                             │
     │ │ Queue     │                 │                                                                    │
     │      │                                                                                             │
     │ └───────────┴─────────────────┴────────────────────────────────────────────────────────────────────│
     │ ─────┘                                                                                             │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Architecture                                                                                       │
     │                                                                                                    │
     │ ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐                                │
     │ │   Next.js UI    │────▶│  FastAPI Backend │────▶│   PostgreSQL    │                               │
     │ │   (Dashboard)   │     │   (REST API)     │     │   (Lead Data)   │                               │
     │ └─────────────────┘     └────────┬─────────┘     └─────────────────┘                               │
     │                                  │                                                                 │
     │                         ┌────────▼─────────┐                                                       │
     │                         │  Celery Workers  │                                                       │
     │                         │  (Scraping Jobs) │                                                       │
     │                         └────────┬─────────┘                                                       │
     │                                  │                                                                 │
     │               ┌──────────────────┼──────────────────┐                                              │
     │               ▼                  ▼                  ▼                                              │
     │         ┌──────────┐      ┌──────────┐      ┌──────────┐                                           │
     │         │  Google  │      │ Instagram│      │  TikTok  │                                           │
     │         │  Search  │      │  Scraper │      │  Scraper │                                           │
     │         └──────────┘      └──────────┘      └──────────┘                                           │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Core Features                                                                                      │
     │                                                                                                    │
     │ 1. Store Discovery Engine                                                                          │
     │                                                                                                    │
     │ Sources:                                                                                           │
     │ - Google Search: Query site:myshopify.com OR site:*.myshopify.com + [niche] + [location]           │
     │ - Instagram: Scrape bio links for Shopify URLs from niche hashtags/accounts                        │
     │ - TikTok: Extract shop links from profiles in target niches                                        │
     │                                                                                                    │
     │ Methods:                                                                                           │
     │ - Free: Direct scraping with Playwright + rotating proxies                                         │
     │ - Paid: SerpAPI for Google (more reliable, avoids blocks)                                          │
     │                                                                                                    │
     │ 2. Data Extraction (per store)                                                                     │
     │ ┌───────────┬─────────────────────────────────────────────────────┐                                │
     │ │ Category  │                     Data Points                     │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Basic     │ Store name, URL, domain, description, logo          │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Contact   │ Email (from /pages/contact, footer), phone, address │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Social    │ Instagram, Facebook, Twitter, TikTok, YouTube links │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Products  │ Product count, categories, price range, bestsellers │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Business  │ Founded date, location/country, currency            │                                │
     │ ├───────────┼─────────────────────────────────────────────────────┤                                │
     │ │ Technical │ Shopify apps installed, theme, payment methods      │                                │
     │ └───────────┴─────────────────────────────────────────────────────┘                                │
     │ 3. Web Dashboard                                                                                   │
     │                                                                                                    │
     │ - Search Page: Input niche keywords + location filters                                             │
     │ - Results Table: Sortable, filterable columns for all data points                                  │
     │ - Lead Detail View: Full store profile with all extracted data                                     │
     │ - Saved Searches: History of previous searches                                                     │
     │ - Export: CSV/Excel download of filtered results                                                   │
     │                                                                                                    │
     │ 4. Background Processing                                                                           │
     │                                                                                                    │
     │ - Queue-based scraping to handle rate limits                                                       │
     │ - Progress tracking for active searches                                                            │
     │ - Retry logic for failed extractions                                                               │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Database Schema                                                                                    │
     │                                                                                                    │
     │ -- Stores table (main leads)                                                                       │
     │ stores (                                                                                           │
     │   id, url, domain, name, description, logo_url,                                                    │
     │   email, phone, address, city, country,                                                            │
     │   instagram, facebook, twitter, tiktok,                                                            │
     │   product_count, price_min, price_max,                                                             │
     │   niche_tags, apps_detected, theme,                                                                │
     │   discovered_via, discovered_at, last_scraped                                                      │
     │ )                                                                                                  │
     │                                                                                                    │
     │ -- Search jobs                                                                                     │
     │ search_jobs (                                                                                      │
     │   id, query, niche, location, status,                                                              │
     │   stores_found, created_at, completed_at                                                           │
     │ )                                                                                                  │
     │                                                                                                    │
     │ -- Search results (many-to-many)                                                                   │
     │ search_results (                                                                                   │
     │   search_id, store_id                                                                              │
     │ )                                                                                                  │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Implementation Phases                                                                              │
     │                                                                                                    │
     │ Phase 1: Project Setup & Core Backend                                                              │
     │                                                                                                    │
     │ - Initialize Python project with FastAPI                                                           │
     │ - Set up PostgreSQL database with SQLAlchemy/Alembic                                               │
     │ - Create database models and migrations                                                            │
     │ - Set up Celery + Redis for task queue                                                             │
     │ - Build basic API endpoints (CRUD for stores, searches)                                            │
     │                                                                                                    │
     │ Phase 2: Scraping Engine                                                                           │
     │                                                                                                    │
     │ - Build Google search scraper (Playwright-based)                                                   │
     │ - Implement Shopify store data extractor                                                           │
     │ - Add Instagram bio link scraper                                                                   │
     │ - Add TikTok profile scraper                                                                       │
     │ - Implement proxy rotation for rate limit handling                                                 │
     │ - Add SerpAPI integration (optional paid tier)                                                     │
     │                                                                                                    │
     │ Phase 3: Frontend Dashboard                                                                        │
     │                                                                                                    │
     │ - Initialize Next.js project                                                                       │
     │ - Build search interface (niche + location inputs)                                                 │
     │ - Create results table with filtering/sorting (using TanStack Table)                               │
     │ - Add lead detail view/modal                                                                       │
     │ - Implement search history page                                                                    │
     │ - Add CSV/Excel export functionality                                                               │
     │                                                                                                    │
     │ Phase 4: Integration & Polish                                                                      │
     │                                                                                                    │
     │ - Connect frontend to backend API                                                                  │
     │ - Add real-time progress updates (WebSocket or polling)                                            │
     │ - Implement error handling and retry logic                                                         │
     │ - Add rate limiting and request throttling                                                         │
     │ - Basic authentication (if needed)                                                                 │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Key Files Structure                                                                                │
     │                                                                                                    │
     │ leadgen/                                                                                           │
     │ ├── backend/                                                                                       │
     │ │   ├── app/                                                                                       │
     │ │   │   ├── main.py                    # FastAPI app entry                                         │
     │ │   │   ├── core/                                                                                  │
     │ │   │   │   ├── config.py              # Centralized settings (DRY)                                │
     │ │   │   │   └── dependencies.py        # Dependency injection (SOLID-D)                            │
     │ │   │   ├── api/                                                                                   │
     │ │   │   │   └── routes/                                                                            │
     │ │   │   │       ├── stores.py                                                                      │
     │ │   │   │       └── searches.py                                                                    │
     │ │   │   ├── models/                    # SQLAlchemy models                                         │
     │ │   │   ├── schemas/                   # Pydantic schemas                                          │
     │ │   │   ├── repositories/              # Data access layer (SOLID-S)                               │
     │ │   │   │   ├── base.py                # Abstract base (SOLID-O/L)                                 │
     │ │   │   │   ├── store_repository.py                                                                │
     │ │   │   │   └── search_repository.py                                                               │
     │ │   │   ├── services/                  # Business logic (SOLID-S)                                  │
     │ │   │   │   ├── store_service.py                                                                   │
     │ │   │   │   └── search_service.py                                                                  │
     │ │   │   ├── scrapers/                                                                              │
     │ │   │   │   ├── base.py                # Abstract scraper (SOLID-O/L/I)                            │
     │ │   │   │   ├── google.py                                                                          │
     │ │   │   │   ├── shopify.py                                                                         │
     │ │   │   │   ├── instagram.py                                                                       │
     │ │   │   │   └── tiktok.py                                                                          │
     │ │   │   ├── tasks/                     # Celery tasks                                              │
     │ │   │   └── db/                                                                                    │
     │ │   ├── requirements.txt                                                                           │
     │ │   └── alembic/                                                                                   │
     │ │                                                                                                  │
     │ ├── frontend/                          # ATOMIC DESIGN ARCHITECTURE                                │
     │ │   ├── src/                                                                                       │
     │ │   │   ├── app/                       # Next.js app router (pages)                                │
     │ │   │   │   ├── page.tsx               # Home/Search page                                          │
     │ │   │   │   ├── leads/page.tsx         # Results page                                              │
     │ │   │   │   └── leads/[id]/page.tsx    # Detail page                                               │
     │ │   │   │                                                                                          │
     │ │   │   ├── components/                                                                            │
     │ │   │   │   ├── atoms/                 # Basic building blocks                                     │
     │ │   │   │   │   ├── Button.tsx                                                                     │
     │ │   │   │   │   ├── Input.tsx                                                                      │
     │ │   │   │   │   ├── Badge.tsx                                                                      │
     │ │   │   │   │   ├── Spinner.tsx                                                                    │
     │ │   │   │   │   └── Icon.tsx                                                                       │
     │ │   │   │   │                                                                                      │
     │ │   │   │   ├── molecules/             # Simple combinations                                       │
     │ │   │   │   │   ├── SearchInput.tsx    # Input + Button                                            │
     │ │   │   │   │   ├── FilterChip.tsx     # Badge + close icon                                        │
     │ │   │   │   │   ├── StatCard.tsx       # Icon + label + value                                      │
     │ │   │   │   │   └── SocialLink.tsx     # Icon + link                                               │
     │ │   │   │   │                                                                                      │
     │ │   │   │   ├── organisms/             # Complex UI sections                                       │
     │ │   │   │   │   ├── SearchForm.tsx     # Multiple molecules                                        │
     │ │   │   │   │   ├── LeadsTable.tsx     # Table with sorting/filtering                              │
     │ │   │   │   │   ├── LeadCard.tsx       # Store preview card                                        │
     │ │   │   │   │   ├── FilterPanel.tsx    # All filter controls                                       │
     │ │   │   │   │   └── LeadDetail.tsx     # Full store info                                           │
     │ │   │   │   │                                                                                      │
     │ │   │   │   └── templates/             # Page layouts                                              │
     │ │   │   │       ├── DashboardLayout.tsx                                                            │
     │ │   │   │       └── SearchLayout.tsx                                                               │
     │ │   │   │                                                                                          │
     │ │   │   ├── hooks/                     # Reusable hooks (DRY)                                      │
     │ │   │   │   ├── useStores.ts                                                                       │
     │ │   │   │   ├── useSearch.ts                                                                       │
     │ │   │   │   └── useFilters.ts                                                                      │
     │ │   │   │                                                                                          │
     │ │   │   ├── lib/                       # Utilities (DRY)                                           │
     │ │   │   │   ├── api.ts                 # API client                                                │
     │ │   │   │   ├── formatters.ts          # Data formatting                                           │
     │ │   │   │   └── validators.ts          # Input validation                                          │
     │ │   │   │                                                                                          │
     │ │   │   └── types/                     # TypeScript types                                          │
     │ │   │       └── index.ts                                                                           │
     │ │   │                                                                                              │
     │ │   └── package.json                                                                               │
     │ │                                                                                                  │
     │ └── docker-compose.yml                                                                             │
     │                                                                                                    │
     │ ---                                                                                                │
     │ Verification Plan                                                                                  │
     │                                                                                                    │
     │ 1. Backend API: Test endpoints with curl/Postman                                                   │
     │ 2. Scraping: Run scrapers against known Shopify stores                                             │
     │ 3. Database: Verify data persistence and queries                                                   │
     │ 4. Frontend: Manual testing of search flow and filtering                                           │
     │ 5. End-to-end: Complete search → scrape → view → export flow                                       │
     │                                                                                                    │
     │ ---                                                                                                │
     │ External Dependencies                                                                              │
     │ ┌────────────┬──────────────────────────┬───────────────────────────┐                              │
     │ │  Service   │         Purpose          │         Free Tier         │                              │
     │ ├────────────┼──────────────────────────┼───────────────────────────┤                              │
     │ │ SerpAPI    │ Google search (optional) │ 100 searches/month        │                              │
     │ ├────────────┼──────────────────────────┼───────────────────────────┤                              │
     │ │ Proxies    │ Avoid IP blocks          │ Limited free options      │                              │
     │ ├────────────┼──────────────────────────┼───────────────────────────┤                              │
     │ │ PostgreSQL │ Database                 │ Local or free Supabase    │                              │
     │ ├────────────┼──────────────────────────┼───────────────────────────┤                              │
     │ │ Redis      │ Task queue               │ Local or free Redis Cloud │                              │
     │ └────────────┴──────────────────────────┴───────────────────────────┘                              │
     │ ---                                                                                                │
     │ Risks & Mitigations                                                                                │
     │ ┌─────────────────────────┬───────────────────────────────────────────────┐                        │
     │ │          Risk           │                  Mitigation                   │                        │
     │ ├─────────────────────────┼───────────────────────────────────────────────┤                        │
     │ │ Google blocks scraping  │ Use SerpAPI or rotate proxies                 │                        │
     │ ├─────────────────────────┼───────────────────────────────────────────────┤                        │
     │ │ Instagram rate limits   │ Slow scraping, use proxies                    │                        │
     │ ├─────────────────────────┼───────────────────────────────────────────────┤                        │
     │ │ Shopify store detection │ Check for Shopify-specific markers            │                        │
     │ ├─────────────────────────┼───────────────────────────────────────────────┤                        │
     │ │ Data freshness          │ Add "last scraped" tracking, re-scrape option │                        │
     │ └─────────────────────────┴───────────────────────────────────────────────┘    

     Phase 2



 Phase 1 complete. Here's the structure created:

  leadgen/
  ├── .gitignore
  ├── docker-compose.yml
  └── backend/
      ├── Dockerfile
      ├── requirements.txt
      ├── alembic.ini
      ├── .env.example
      ├── alembic/
      │   ├── env.py
      │   ├── script.py.mako
      │   └── versions/
      │       └── 001_initial_tables.py
      └── app/
          ├── main.py                 # FastAPI entry point
          ├── core/
          │   ├── config.py           # Settings (pydantic-settings)
          │   └── dependencies.py     # Dependency injection
          ├── db/
          │   └── database.py         # SQLAlchemy setup
          ├── models/
          │   ├── store.py            # Store model
          │   └── search.py           # SearchJob, SearchResult models
          ├── schemas/
          │   ├── store.py            # Store Pydantic schemas
          │   └── search.py           # Search Pydantic schemas
          ├── repositories/
          │   ├── base.py             # Base repository (CRUD)
          │   ├── store_repository.py
          │   └── search_repository.py
          ├── services/
          │   ├── store_service.py
          │   └── search_service.py
          ├── scrapers/
          │   └── base.py             # Abstract scraper classes
          ├── tasks/
          │   ├── celery_app.py       # Celery configuration
          │   └── search_tasks.py     # Background tasks
          └── api/routes/
              ├── stores.py           # Store CRUD endpoints
              └── searches.py         # Search endpoints

  To run locally:
  cd backend
  pip install -r requirements.txt
  docker-compose up db redis -d
  alembic upgrade head
  uvicorn app.main:app --reload

  API endpoints available at http://localhost:8000:
  - GET /api/v1/stores - List/search stores
  - POST /api/v1/stores - Create store
  - GET /api/v1/searches - List searches
  - POST /api/v1/searches - Create search job

  Ready for Phase 2 (Scraping Engine)?