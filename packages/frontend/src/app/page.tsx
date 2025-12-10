import Link from 'next/link';
import { Button } from '@/components/ui/button';

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

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-12">
          <Button asChild size="lg">
            <Link href="/login">Sign In</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/register">Create Account</Link>
          </Button>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-semibold mb-2">Real-time Insights</h3>
            <p className="text-sm text-muted-foreground">
              Get AI-powered analysis of stock news for major tech companies.
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-semibold mb-2">Smart RAG Pipeline</h3>
            <p className="text-sm text-muted-foreground">
              Advanced retrieval-augmented generation for accurate responses.
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-semibold mb-2">Chat History</h3>
            <p className="text-sm text-muted-foreground">
              Keep track of your conversations and revisit previous insights.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
