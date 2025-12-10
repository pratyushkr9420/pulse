'use client';

/**
 * Header component with navigation and authentication controls.
 */

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';

export function Header() {
  const { isAuthenticated, logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    // Use window.location for full page reload to trigger middleware
    // This ensures cookie is cleared and middleware redirects properly
    window.location.href = '/login';
  };

  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <h1 className="text-2xl font-bold text-foreground">Pulse</h1>
          <span className="text-xs text-muted-foreground hidden sm:inline">
            Stock News Assistant
          </span>
        </Link>

        <nav className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link href="/chat">Chat</Link>
              </Button>
              <span className="text-sm text-muted-foreground hidden md:inline">
                {user?.username}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                data-testid="logout-button"
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link href="/login">Sign In</Link>
              </Button>
              <Button asChild size="sm">
                <Link href="/register">Sign Up</Link>
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
