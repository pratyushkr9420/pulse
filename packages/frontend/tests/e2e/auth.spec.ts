import { test, expect } from '@playwright/test';

// Generate unique username for each test run to avoid conflicts
const generateUsername = () => `testuser_${Date.now()}_${Math.random().toString(36).substring(7)}`;

test.describe('Authentication', () => {
  test('user can register', async ({ page }) => {
    const username = generateUsername();

    await page.goto('/register');

    // Wait for form to be ready
    await page.waitForSelector('[name="username"]', { timeout: 5000 });

    await page.fill('[name="username"]', username);
    await page.fill('[name="password"]', 'password123');
    await page.fill('[name="confirmPassword"]', 'password123');

    await page.click('button[type="submit"]');

    // Production UX: Registration auto-logs in and redirects to /chat
    // Use waitForURL to properly wait for async navigation
    // Increase timeout to handle slow backend responses
    await page.waitForURL('/chat', { timeout: 20000 });
    // Wait for chat interface to be ready (ensures page fully loaded)
    await page.waitForSelector('textarea[placeholder="Ask about stock news..."]', { timeout: 15000 });
  });

  test('user can login', async ({ page }) => {
    // First register a user
    const username = generateUsername();
    await page.goto('/register');
    await page.fill('[name="username"]', username);
    await page.fill('[name="password"]', 'password123');
    await page.fill('[name="confirmPassword"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat', { timeout: 10000 });

    // Logout
    await page.click('[data-testid="logout-button"]');
    await page.waitForURL('/login', { timeout: 10000 });

    // Now test login
    await page.goto('/login');
    await page.fill('[name="username"]', username);
    await page.fill('[name="password"]', 'password123');

    await page.click('button[type="submit"]');

    // Wait for async login and navigation
    await page.waitForURL('/chat', { timeout: 10000 });
    // Wait for chat interface to be ready (ensures page fully loaded)
    await page.waitForSelector('textarea[placeholder="Ask about stock news..."]', { timeout: 15000 });
  });

  test('protected route redirects to login', async ({ page }) => {
    // Clear any existing auth state
    await page.context().clearCookies();
    // Use try-catch for localStorage.clear() as it can throw security errors in some browsers
    try {
      await page.evaluate(() => localStorage.clear());
    } catch (e) {
      // Ignore security errors - cookies are already cleared which is sufficient
    }

    await page.goto('/chat');

    await expect(page).toHaveURL('/login');
  });

  test('shows error on invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="username"]', 'wronguser');
    await page.fill('[name="password"]', 'wrongpassword');

    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid')).toBeVisible();
  });

  test('user can logout', async ({ page }) => {
    // Register and login first
    const username = generateUsername();
    await page.goto('/register');
    await page.fill('[name="username"]', username);
    await page.fill('[name="password"]', 'password123');
    await page.fill('[name="confirmPassword"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat', { timeout: 10000 });

    // Logout
    await page.click('[data-testid="logout-button"]');

    // Wait for async logout and navigation
    await page.waitForURL('/login', { timeout: 10000 });
  });
});
