'use client';

/**
 * Header component with navigation and authentication controls.
 */

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
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-foreground">Pulse</h1>
          <span className="text-xs text-muted-foreground hidden sm:inline">
            Stock News Assistant
          </span>
        </div>

        {isAuthenticated && (
          <div className="flex items-center gap-4">
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
          </div>
        )}
      </div>
    </header>
  );
}
