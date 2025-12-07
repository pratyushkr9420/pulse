import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('user can register', async ({ page }) => {
    await page.goto('/register');

    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.fill('[name="confirmPassword"]', 'password123');

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/login');
  });

  test('user can login', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/chat');
  });

  test('protected route redirects to login', async ({ page }) => {
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
    // Login first
    await page.goto('/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');

    // Logout
    await page.click('[data-testid="logout-button"]');

    await expect(page).toHaveURL('/login');
  });
});
