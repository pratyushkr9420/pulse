export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4">
          Welcome to <span className="text-primary">Pulse</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Your AI-powered stock news assistant. Get instant insights on AAPL, MSFT, AMZN, NFLX, NVDA, INTC, and IBM.
        </p>
      </div>
    </div>
  );
}
