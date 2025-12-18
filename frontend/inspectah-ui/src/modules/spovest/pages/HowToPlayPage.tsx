import { Link } from 'react-router-dom';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpTestimonialCard } from '../components/ui/Card';
import type { SpTestimonial } from '../types';

const steps = [
  {
    number: '01',
    title: 'Create Your Account',
    description: 'Sign up for free in less than a minute. Verify your email and you\'re ready to start trading.',
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
  },
  {
    number: '02',
    title: 'Deposit Funds',
    description: 'Add funds to your account using credit/debit cards, bank transfer, or cryptocurrency.',
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    number: '03',
    title: 'Watch the Market',
    description: 'Analyze player prices, track performance trends, and identify trading opportunities.',
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    number: '04',
    title: 'Make Your Trade',
    description: 'Buy shares of athletes you believe will perform well. Sell when prices rise for profit.',
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
      </svg>
    ),
  },
  {
    number: '05',
    title: 'Collect Earnings',
    description: 'Earn dividends on game days based on player performance. Withdraw your profits anytime.',
    icon: (
      <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
];

const testimonials: SpTestimonial[] = [
  {
    id: '1',
    name: 'Mike Johnson',
    location: 'Texas, USA',
    text: 'The learning curve was super easy. Within a week, I was making profitable trades consistently.',
    rating: 5,
  },
  {
    id: '2',
    name: 'Sarah Williams',
    location: 'Florida, USA',
    text: 'I love how the tutorial walked me through everything. Now I trade like a pro!',
    rating: 5,
  },
  {
    id: '3',
    name: 'Chris Martinez',
    location: 'California, USA',
    text: 'The video tutorial made everything crystal clear. Highly recommend watching it before you start.',
    rating: 5,
  },
];

export function SpHowToPlayPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/30 via-slate-900 to-cyan-900/20" />
        <div className="absolute top-20 right-10 w-72 h-72 bg-cyan-600/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8">
            <Link to="/spovest" className="hover:text-white transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white">How to Play</span>
          </nav>

          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              How to{' '}
              <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                Play & Win
              </span>
            </h1>
            <p className="text-xl text-slate-300">
              Follow these simple steps to start trading athletes and building your portfolio.
            </p>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <SpCard variant="bordered" padding="none" className="overflow-hidden">
            <div className="aspect-video bg-gradient-to-br from-violet-600/20 to-cyan-600/20 flex items-center justify-center">
              <button className="w-20 h-20 rounded-full bg-white/10 backdrop-blur flex items-center justify-center hover:bg-white/20 transition-colors group">
                <svg className="w-10 h-10 text-white ml-1 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </button>
            </div>
            <div className="p-6 text-center">
              <h3 className="text-lg font-bold text-white mb-2">Watch Our Tutorial</h3>
              <p className="text-slate-400">Learn how to trade in just 2 minutes</p>
            </div>
          </SpCard>
        </div>
      </section>

      {/* Steps */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">5 Simple Steps</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Getting started with Spovest is easy. Follow these steps and you'll be trading in minutes.
            </p>
          </div>

          <div className="space-y-8">
            {steps.map((step, index) => (
              <div
                key={step.number}
                className={`flex flex-col md:flex-row items-center gap-8 ${
                  index % 2 === 1 ? 'md:flex-row-reverse' : ''
                }`}
              >
                {/* Content */}
                <SpCard variant="gradient" hover className="flex-1 md:max-w-lg">
                  <div className="flex items-start gap-6">
                    <div className="flex-shrink-0">
                      <span className="text-5xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                        {step.number}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                      <p className="text-slate-400">{step.description}</p>
                    </div>
                  </div>
                </SpCard>

                {/* Icon */}
                <div className="flex-shrink-0 w-32 h-32 rounded-full bg-gradient-to-br from-violet-600/20 to-cyan-600/20 border border-slate-700/50 flex items-center justify-center text-violet-400">
                  {step.icon}
                </div>

                {/* Empty space for alternating layout */}
                <div className="flex-1 md:max-w-lg hidden md:block" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tips */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Pro Tips for Success</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Expert strategies to maximize your trading potential.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Diversify Your Portfolio',
                description: 'Don\'t put all your eggs in one basket. Spread investments across multiple athletes and sports.',
                icon: '📊',
              },
              {
                title: 'Follow the News',
                description: 'Stay updated on injuries, trades, and team changes that can affect player prices.',
                icon: '📰',
              },
              {
                title: 'Buy the Dip',
                description: 'When a star player has a bad game, it might be the perfect time to buy low.',
                icon: '📉',
              },
              {
                title: 'Track Performance Trends',
                description: 'Use our analytics to identify players on hot streaks before prices spike.',
                icon: '🔥',
              },
              {
                title: 'Set Price Alerts',
                description: 'Get notified when players hit your target buy or sell prices.',
                icon: '🔔',
              },
              {
                title: 'Start Small',
                description: 'Begin with smaller trades to learn the market before making bigger moves.',
                icon: '🎯',
              },
            ].map((tip) => (
              <SpCard key={tip.title} variant="bordered" hover>
                <span className="text-4xl mb-4 block">{tip.icon}</span>
                <h3 className="text-lg font-bold text-white mb-2">{tip.title}</h3>
                <p className="text-slate-400 text-sm">{tip.description}</p>
              </SpCard>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Success Stories</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Hear from traders who started just like you.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <SpTestimonialCard key={testimonial.id} testimonial={testimonial} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 via-transparent to-cyan-600/20" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Start Your Journey?
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            Sign up now and get a free stock to practice your trading skills.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/spovest/signup">
              <SpButton size="xl" className="shadow-xl shadow-violet-500/30">
                Start Trading
              </SpButton>
            </Link>
            <Link to="/spovest/faq">
              <SpButton variant="outline" size="xl">
                Read FAQ
              </SpButton>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
