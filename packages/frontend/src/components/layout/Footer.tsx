/**
 * Footer component - Application footer with info and links.
 */

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-muted/30">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-muted-foreground">
            <p>
              Pulse - Stock News Chatbot
            </p>
            <p className="text-xs mt-1">
              Covering: AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM
            </p>
          </div>

          <div className="text-xs text-muted-foreground">
            © {currentYear} Pulse. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
