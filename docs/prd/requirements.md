# Requirements

## Functional

**FR1:** The system shall provide user registration and authentication via email/password and OAuth integration for Facebook, Google, and Apple IDs, maintaining personalized learning progress across sessions.

**FR2:** The system shall enable users to select two languages from available options stored in the languages database table to create their native and target language pair.

**FR3:** The system shall provide a searchable movie catalog where users can find movies by text title search or browse alphabetically by clicking first letter groups (e.g., clicking "H" shows all movies starting with H like "Happy Gilmore").

**FR4:** The system shall display synchronized dual-language subtitles side-by-side in text format without movie playback functionality.

**FR5:** The system shall track and persist user learning progress including lines completed, time spent, movies viewed, and session history across login sessions.

**FR6:** The system shall provide subtitle file storage and retrieval capabilities supporting efficient search and streaming of subtitle content for selected movies.

**FR8:** The system shall allow users to bookmark specific subtitle lines or scenes for later review and practice.

## Non Functional

**NFR1:** The system shall achieve initial page load times under 3 seconds and subtitle synchronization response times under 1 second to maintain user engagement.

**NFR2:** The system shall support 100+ concurrent users during peak usage without performance degradation or subtitle timing drift.

**NFR3:** The system shall maintain 99.5% uptime availability to ensure consistent access for daily learning routines.

**NFR4:** The system shall implement secure session management, input sanitization, and HTTPS enforcement to protect user data and privacy.

**NFR5:** The system shall provide responsive web design compatible with modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) and optimal for desktop/laptop usage.

**NFR6:** The system shall follow GDPR-compliant user data handling practices including data portability and deletion capabilities.

**NFR7:** The system shall implement graceful error handling and user-friendly error messages to minimize learning session interruptions.

**NFR8:** The system shall support database migration from SQLite to PostgreSQL as user base scales beyond single-server capacity.
