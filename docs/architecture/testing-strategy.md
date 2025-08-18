# Testing Strategy

## Testing Pyramid

```
                  Manual E2E Tests
                 /                \
            Integration Tests (API)
               /                    \
          Backend Unit Tests    Frontend Unit Tests
```

## Test Organization

### Backend Tests
```
tests/
├── conftest.py                     # pytest configuration and fixtures
├── test_models/
│   ├── test_user.py               # User model and authentication tests
│   ├── test_subtitle.py           # Subtitle schema model tests
│   ├── test_progress.py           # Progress tracking model tests
│   └── test_bookmark.py           # Bookmark model tests
├── test_services/
│   ├── test_auth_service.py       # Authentication business logic tests
│   ├── test_subtitle_service.py   # Subtitle processing and caching tests
│   ├── test_progress_service.py   # Progress calculation tests
│   └── test_content_service.py    # Movie discovery and filtering tests
├── test_api/
│   ├── test_auth_endpoints.py     # Authentication API tests
│   ├── test_subtitle_endpoints.py # Subtitle content API tests
│   ├── test_progress_endpoints.py # Progress tracking API tests
│   └── test_movie_endpoints.py    # Movie discovery API tests
└── test_integration/
    ├── test_learning_flow.py      # Complete learning session tests
    ├── test_oauth_integration.py  # OAuth provider integration tests
    └── test_database_performance.py # SQLite performance tests
```

### Frontend Tests (Manual)
```
manual_tests/
├── ui_checklist.md                # Manual UI testing checklist
├── browser_compatibility.md       # Cross-browser testing guide
├── responsive_testing.md          # Mobile/tablet testing checklist
├── accessibility_testing.md       # WCAG compliance verification
└── performance_testing.md         # Frontend performance benchmarks
```

### E2E Tests (Manual)
```
e2e_scenarios/
├── new_user_journey.md            # First-time user flow testing
├── returning_user_flow.md         # Existing user scenarios
├── learning_session_scenarios.md  # Core subtitle learning tests
├── oauth_flows.md                 # Social authentication testing
└── error_scenarios.md             # Error handling and recovery tests
```
