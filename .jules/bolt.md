## 2024-05-23 - Blocking Async Operations
**Learning:** In FastAPI, `async def` endpoints run on the main event loop. Calling synchronous, blocking operations (like external API calls or heavy computation) directly within these endpoints blocks the entire server, preventing it from handling other requests.
**Action:** Always use asynchronous versions of I/O bound libraries (e.g., `await model.generate_content_async`) or run synchronous blocking code in a thread pool using `run_in_executor` to keep the event loop responsive.

## 2024-05-25 - Blocking DB in Async Telegram Bot
**Learning:** `python-telegram-bot` handlers are `async` and run on the event loop. Executing synchronous SQLAlchemy `db.commit()` calls directly inside a handler blocks the loop, freezing the bot (and any shared process like FastAPI).
**Action:** Offload synchronous DB operations to a thread using `asyncio.to_thread` (standard lib) instead of `fastapi.concurrency` if you want to keep the bot code generic and independent of the web framework.

## 2025-05-27 - PYTHONPATH for Mixed Imports
**Learning:** When tests import both `backend.main` (treating backend as package) and `main` (treating backend as root), `PYTHONPATH` must be set to `.:backend` (or equivalent) to satisfy both import styles.
**Action:** Use `PYTHONPATH=.:backend pytest tests/` when running tests in a repo with mixed import styles.

## 2025-02-27 - UploadFile Validation Blocking
**Learning:** `UploadFile` validation using `python-magic` and file seeking is synchronous and CPU/IO bound. In FastAPI async endpoints, this blocks the event loop.
**Action:** Wrap file validation logic in `run_in_threadpool` and await it.

## 2026-02-04 - Redundant Image Processing Cycles
**Learning:** Performing validation, resizing, and EXIF stripping as discrete steps in an image pipeline causes multiple redundant Decode-Process-Encode cycles. This is particularly expensive in cloud environments with limited CPU.
**Action:** Unify all image transformations into a single pass (`process_uploaded_image`) to ensure the image is only decoded and encoded once.

## 2026-02-05 - Leaderboard Aggregation Caching
**Learning:** Aggregation queries (`COUNT`, `SUM`, `GROUP BY`) on the primary application tables grow O(N) with the number of reports. On high-traffic civic platforms, these are frequent bottlenecks.
**Action:** Implement short-lived (5 min) caching for leaderboard results. Use database-level aggregations and column selection (`db.query(cols)`) instead of loading full model instances.

## 2026-02-05 - Schema Inheritance vs Redefinition
**Learning:** Redefining similar schemas (e.g., `IssueSummaryResponse` vs `IssueResponse`) leads to maintenance overhead and potential inconsistencies in API responses.
**Action:** Use Pydantic inheritance to define a base summary schema and extend it for detailed views, ensuring consistent data structures across the app.

## 2026-02-06 - Column Projection vs Full ORM Loading
**Learning:** Loading full SQLAlchemy model instances for list views or spatial checks is significantly slower and more memory-intensive than selecting only required columns, especially when tables contain large JSON or Text fields.
**Action:** Use `db.query(Model.col1, Model.col2)` for read-heavy list endpoints and spatial candidate searches. Note that projected results are immutable `Row` objects, so use `db.query(Model).filter(...).update()` for atomic modifications.

## 2026-02-15 - React Component Definition & Navigation Props
**Learning:** Lazy loading components in React (`React.lazy`) creates a dependency on the parent component's scope. If the parent references undefined layout components inline, the app may crash silently or throw confusing errors. Additionally, hardcoding navigation paths (like `navigate('/')`) inside reusable components limits their reuse in different contexts.
**Action:** Explicitly define or import all layout components before lazy loading routes. Pass navigation handlers (like `onBack`) as props to child components to decouple them from specific routing logic.

## 2026-02-28 - Netlify Build & Lockfile Conflicts
**Learning:** Checking in `package-lock.json` generated on one OS/Node version can cause `npm install` failures or build errors on Netlify/CI environments due to platform-specific optional dependencies or integrity checksum mismatches. Additionally, aggressive linting rules (like `no-unused-vars` erroring on JSX imports) can block builds if CI treats warnings as errors.
**Action:** If experiencing persistent CI build failures related to dependencies, try removing `package-lock.json` to force a clean install. Ensure linting rules are set to `warn` for non-critical stylistic checks in CI environments.
