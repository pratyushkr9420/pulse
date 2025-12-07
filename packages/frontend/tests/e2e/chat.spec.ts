import { test, expect } from '@playwright/test';

test.describe('Chat', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');
  });

  test('can send a message', async ({ page }) => {
    await page.fill('[data-testid="chat-input"]', 'What is the latest AAPL news?');
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="chat-message"]')).toBeVisible();
  });

  test('displays sources with clickable links', async ({ page }) => {
    await page.fill('[data-testid="chat-input"]', 'Tell me about Apple');
    await page.click('[data-testid="send-button"]');

    // Wait for sources
    const sourceLink = page.locator('[data-testid="source-link"]').first();
    await expect(sourceLink).toBeVisible();
    await expect(sourceLink).toHaveAttribute('target', '_blank');
  });

  test('can filter by ticker', async ({ page }) => {
    await page.click('[data-testid="ticker-filter"]');
    await page.click('[data-value="AAPL"]');

    await page.fill('[data-testid="chat-input"]', 'Latest news');
    await page.click('[data-testid="send-button"]');

    // Response should be about AAPL
    await expect(page.locator('text=AAPL')).toBeVisible();
  });

  test('can change retriever type', async ({ page }) => {
    await page.click('[data-testid="retriever-type-select"]');
    await page.click('[data-value="hybrid"]');

    await page.fill('[data-testid="chat-input"]', 'NVDA news');
    await page.click('[data-testid="send-button"]');

    await expect(page.locator('[data-testid="chat-message"]')).toBeVisible();
  });

  test('shows chat history', async ({ page }) => {
    // Send a message
    await page.fill('[data-testid="chat-input"]', 'Test message');
    await page.click('[data-testid="send-button"]');

    // Reload page
    await page.reload();

    // History should still be visible
    await expect(page.locator('text=Test message')).toBeVisible();
  });
});
