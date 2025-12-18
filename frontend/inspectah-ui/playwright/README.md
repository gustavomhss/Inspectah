# Playwright E2E Tests

Comprehensive end-to-end tests for the Inspectah frontend application.

## Overview

| Metric | Value |
|--------|-------|
| **Total Test Files** | 17 |
| **Total Test Cases** | 836 |
| **Total Lines of Code** | 11,166 |

## Test Files

### Core Module Tests

| File | Module | Tests | Description |
|------|--------|-------|-------------|
| `auth.pw.ts` | Auth | 20 | Login, validation, session management, accessibility |
| `admin.pw.ts` | Admin | 45 | Admin dashboard, cases list, sources list, navigation |
| `consult.pw.ts` | Public | 35 | Public consultation page, search, results display |
| `agents.pw.ts` | Agents | 40 | Agent list, detail, committees, model policy |
| `guardian.pw.ts` | Guardian | 50 | Guardian cockpit, claim review, batch operations |
| `ingestion.pw.ts` | Ingestion | 35 | Ingestion monitoring, source health, operations |
| `ops.pw.ts` | Ops | 45 | Ops cockpit, system health, alerts, incidents |
| `sources.pw.ts` | Sources | 40 | Sources CRUD, health monitoring, debunker |
| `console.pw.ts` | Console | 40 | Truth Console, Agent Studio, Incident Console |
| `cases.pw.ts` | Cases | 50 | Case timeline, X-ray panels, case detail |

### Feature Tests

| File | Feature | Tests | Description |
|------|---------|-------|-------------|
| `spovest.pw.ts` | Spovest | 100+ | All 24 Spovest pages (public, user, admin) |
| `truth-twin.pw.ts` | Truth Twin | 30 | Truth Twin page, provenance, decision blocks |
| `s40_truth_twin.pw.ts` | Sprint 40 | 25 | Sprint 40 Truth Twin specific tests |

### Cross-Cutting Tests

| File | Type | Tests | Description |
|------|------|-------|-------------|
| `edge-cases.pw.ts` | Edge Cases | 60 | Network errors, HTTP status codes, XSS, edge inputs |
| `smoke.pw.ts` | Smoke | 15 | Quick smoke tests for critical paths |
| `full-flows.pw.ts` | Integration | 20 | Complete user journey integration tests |
| `sf2_ui.pw.ts` | SF2 | 5 | SF2 UI specific tests |

## Coverage Areas

### Functional Testing
- Page load validation
- Form submission and validation
- API interactions with mocked responses
- CRUD operations
- Navigation flows
- Search and filtering
- Pagination
- Sorting

### Error Handling
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Internal Server Error
- Network timeout
- Offline mode
- Malformed API responses

### Form Validation
- Empty field validation
- Email format validation
- Password requirements
- Password matching
- Required fields
- Character limits
- XSS prevention
- SQL injection prevention

### Edge Cases
- Empty states (no data)
- Loading states
- Long strings
- Unicode characters
- Special characters
- Boundary values
- Concurrent actions

### Responsive Design
- Mobile (375x667)
- Tablet (768x1024)
- Desktop (1920x1080)

### Accessibility (A11y)
- Keyboard navigation
- Tab order
- Focus management
- ARIA attributes
- Screen reader announcements
- Form labels
- Error announcements

## Running Tests

### Prerequisites

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Commands

```bash
# Run all tests
npx playwright test

# Run specific file
npx playwright test auth.pw.ts

# Run tests matching pattern
npx playwright test -g "Login"

# Run in headed mode (see browser)
npx playwright test --headed

# Run with debug mode
npx playwright test --debug

# Run with UI mode
npx playwright test --ui

# Run specific project (browser)
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Generate HTML report
npx playwright test --reporter=html

# List all tests
npx playwright test --list
```

### Environment Variables

```bash
# Base URL (default: http://localhost:5173)
BASE_URL=http://localhost:5173

# Test timeout (default: 30000ms)
PLAYWRIGHT_TIMEOUT=30000
```

## Test Structure

Each test file follows this structure:

```typescript
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const TEST_TOKEN = '...'; // JWT for authenticated tests

// Helper to setup authenticated session
async function setupAuth(page: Page) {
  await page.addInitScript((token) => {
    localStorage.setItem('auth_token', token);
  }, TEST_TOKEN);
}

test.describe('Module Name', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await page.goto(`${BASE_URL}/path`);
  });

  test('should do something', async ({ page }) => {
    // Test implementation
  });
});
```

## API Mocking

Tests use Playwright's route interception for API mocking:

```typescript
// Mock successful response
await page.route('**/api/endpoint', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ data: 'value' }),
  });
});

// Mock error response
await page.route('**/api/endpoint', async (route) => {
  await route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Internal server error' }),
  });
});
```

## Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Wait for network idle** before assertions
3. **Use conditional checks** for optional elements
4. **Mock API responses** for deterministic tests
5. **Test one thing per test** for clarity
6. **Use descriptive test names** that explain the expected behavior

## Continuous Integration

Tests are configured to run in CI/CD pipelines:

```yaml
# .github/workflows/e2e.yml
- name: Run Playwright tests
  run: npx playwright test
  env:
    CI: true
```

## Debugging

```bash
# Run with trace on
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip

# Run in debug mode
PWDEBUG=1 npx playwright test

# Generate screenshot on failure
npx playwright test --screenshot only-on-failure
```

## Reports

After running tests, view the HTML report:

```bash
npx playwright show-report
```

## Contributing

When adding new tests:

1. Follow existing file naming convention (`module.pw.ts`)
2. Group related tests in `test.describe` blocks
3. Use helper functions for repeated setup
4. Add both positive and negative test cases
5. Include responsive design tests
6. Include accessibility tests
7. Update this README with new coverage areas
