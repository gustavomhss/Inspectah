import { Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpPlayerCard, SpTestimonialCard } from '../components/ui/Card';
import type { SpPlayer, SpTestimonial } from '../types';

// Mock data for demo
const featuredPlayers: SpPlayer[] = [
  {
    id: '1',
    name: 'Stephen Curry',
    firstName: 'Stephen',
    lastName: 'Curry',
    team: 'Golden State Warriors',
    position: 'PG',
    sport: 'NBA',
    price: 1.06,
    priceChange: 0.21,
    priceChangePercent: 11,
    stats: { games: 1, points: 15.6, assists: 2.9, rebounds: 3.6, steals: 1.4, minutes: 28.6, fantasyPoints: 25.6 },
  },
  {
    id: '2',
    name: 'LeBron James',
    firstName: 'LeBron',
    lastName: 'James',
    team: 'Los Angeles Lakers',
    position: 'SF',
    sport: 'NBA',
    price: 1.25,
    priceChange: 0.15,
    priceChangePercent: 8.5,
    stats: { games: 1, points: 22.3, assists: 5.1, rebounds: 7.2, steals: 0.9, minutes: 32.1, fantasyPoints: 35.2 },
  },
  {
    id: '3',
    name: 'Kevin Durant',
    firstName: 'Kevin',
    lastName: 'Durant',
    team: 'Phoenix Suns',
    position: 'SF',
    sport: 'NBA',
    price: 1.18,
    priceChange: -0.08,
    priceChangePercent: -4.2,
    stats: { games: 1, points: 18.9, assists: 3.2, rebounds: 5.8, steals: 0.7, minutes: 30.5, fantasyPoints: 28.4 },
  },
  {
    id: '4',
    name: 'Giannis Antetokounmpo',
    firstName: 'Giannis',
    lastName: 'Antetokounmpo',
    team: 'Milwaukee Bucks',
    position: 'PF',
    sport: 'NBA',
    price: 1.42,
    priceChange: 0.32,
    priceChangePercent: 12.8,
    stats: { games: 1, points: 28.4, assists: 4.8, rebounds: 11.2, steals: 1.1, minutes: 34.2, fantasyPoints: 42.1 },
  },
];

const testimonials: SpTestimonial[] = [
  {
    id: '1',
    name: 'John Smith',
    location: 'New York, USA',
    text: 'Spovest has completely changed how I experience fantasy sports. The ability to trade athletes like stocks makes it so much more engaging and strategic.',
    rating: 5,
  },
  {
    id: '2',
    name: 'Maria Garcia',
    location: 'Los Angeles, USA',
    text: 'I love the real-time price updates and the intuitive interface. Made over $500 in my first month just by following player performance trends.',
    rating: 5,
  },
  {
    id: '3',
    name: 'David Chen',
    location: 'Chicago, USA',
    text: 'The multi-sport support is amazing. I can diversify my portfolio across NBA, NFL, and Soccer all in one platform.',
    rating: 4,
  },
];

const steps = [
  {
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: 'Deposit',
    description: 'Fund your account securely with multiple payment options including cards and crypto.',
  },
  {
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Watch the Market',
    description: 'Track player prices in real-time. Analyze trends and find the best opportunities.',
  },
  {
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
      </svg>
    ),
    title: 'Trade',
    description: 'Buy low, sell high. Build your portfolio and profit from player performance.',
  },
];

export function SpHomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/30 via-slate-900 to-cyan-900/20" />
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-violet-600/20 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
                Trade Athletes Like{' '}
                <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                  Stocks
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-300 mb-8 max-w-xl mx-auto lg:mx-0">
                Spovest is the future of daily fantasy. Buy, sell, and trade shares of your favorite athletes. Build your portfolio and dominate the competition.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link to="/spovest/signup">
                  <SpButton size="xl" className="w-full sm:w-auto">
                    Start Trading
                    <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </SpButton>
                </Link>
                <Link to="/spovest/how-to-play">
                  <SpButton variant="outline" size="xl" className="w-full sm:w-auto">
                    Learn How It Works
                  </SpButton>
                </Link>
              </div>

              {/* Stats */}
              <div className="flex justify-center lg:justify-start gap-8 mt-12">
                {[
                  { value: '50K+', label: 'Active Traders' },
                  { value: '$10M+', label: 'Volume Traded' },
                  { value: '5000+', label: 'Athletes' },
                ].map((stat) => (
                  <div key={stat.label}>
                    <p className="text-2xl sm:text-3xl font-bold text-white">{stat.value}</p>
                    <p className="text-sm text-slate-400">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Right - Featured Player Cards */}
            <div className="hidden lg:grid grid-cols-2 gap-4">
              {featuredPlayers.slice(0, 2).map((player) => (
                <SpPlayerCard key={player.id} player={player} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Featured Athletes Carousel */}
      <section className="py-16 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Trending Athletes</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Discover the hottest players in the market. Track their performance and find your next trade.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredPlayers.map((player) => (
              <SpPlayerCard key={player.id} player={player} showActions />
            ))}
          </div>

          <div className="text-center mt-10">
            <Link to="/spovest/trade">
              <SpButton variant="outline" size="lg">
                View All Athletes
              </SpButton>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Get started in three simple steps and begin trading your favorite athletes.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <SpCard key={index} variant="gradient" hover className="text-center relative">
                {/* Step Number */}
                <div className="absolute -top-4 -right-4 w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-white font-bold shadow-lg">
                  {index + 1}
                </div>

                <div className="text-violet-400 mb-6 flex justify-center">{step.icon}</div>
                <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                <p className="text-slate-400">{step.description}</p>
              </SpCard>
            ))}
          </div>
        </div>
      </section>

      {/* Buy Low, Sell High */}
      <section className="py-20 bg-gradient-to-br from-violet-900/20 via-slate-900 to-cyan-900/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
                Buy Low,{' '}
                <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                  Sell High
                </span>
              </h2>
              <p className="text-lg text-slate-300 mb-6">
                Just like the stock market, player prices fluctuate based on performance. Identify undervalued athletes, buy their shares, and sell when they peak.
              </p>
              <ul className="space-y-4">
                {[
                  'Real-time price updates based on player performance',
                  'Trade 24/7 - no waiting for game day',
                  'Build a diversified portfolio across multiple sports',
                  'Earn dividends on game-day performance',
                ].map((item, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-slate-300">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link to="/spovest/signup">
                  <SpButton size="lg">
                    Get Free Stock
                    <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                    </svg>
                  </SpButton>
                </Link>
              </div>
            </div>

            {/* Chart Placeholder */}
            <div className="bg-slate-800/50 rounded-2xl p-8 border border-slate-700/50">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-sm text-slate-400">Stephen Curry</p>
                  <p className="text-2xl font-bold text-white">$1.06</p>
                </div>
                <span className="px-3 py-1 bg-emerald-400/10 text-emerald-400 text-sm font-medium rounded-full">
                  +11.2%
                </span>
              </div>
              {/* Simple Chart Visualization */}
              <div className="h-48 flex items-end justify-between gap-2">
                {[40, 55, 45, 70, 60, 80, 75, 90, 85, 95, 88, 100].map((height, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-violet-600/50 to-cyan-600/50 rounded-t"
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-4 text-xs text-slate-500">
                <span>12 hours ago</span>
                <span>Now</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Multi-Sports */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Trade Across Multiple Sports</h2>
          <p className="text-slate-400 max-w-2xl mx-auto mb-12">
            Diversify your portfolio with athletes from all major sports leagues.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4">
            {['NBA', 'NFL', 'MLB', 'NHL', 'Soccer', 'Golf', 'ESports'].map((sport) => (
              <Link
                key={sport}
                to={`/spovest/trade/${sport.toLowerCase()}`}
                className={clsx(
                  'p-6 rounded-xl border border-slate-700/50 bg-slate-800/30',
                  'hover:bg-slate-800 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/10',
                  'transition-all duration-300'
                )}
              >
                <span className="text-lg font-bold text-white">{sport}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">What Traders Say</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Join thousands of satisfied traders who are already profiting from Spovest.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <SpTestimonialCard key={testimonial.id} testimonial={testimonial} />
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 via-transparent to-cyan-600/20" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Start Trading?
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            Sign up now and get a free stock to kickstart your portfolio.
          </p>
          <Link to="/spovest/signup">
            <SpButton size="xl" className="shadow-xl shadow-violet-500/30">
              Get Started - It's Free
            </SpButton>
          </Link>
        </div>
      </section>
    </div>
  );
}
