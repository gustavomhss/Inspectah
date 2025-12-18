import { Link } from 'react-router-dom';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpStatCard, SpTeamMemberCard } from '../components/ui/Card';
import type { SpTeamMember } from '../types';

const teamMembers: SpTeamMember[] = [
  { id: '1', name: 'Elijah Ryan', role: 'Co-founder & CEO' },
  { id: '2', name: 'Sammey Kelley', role: 'Co-founder & CTO' },
  { id: '3', name: 'Bobby Smith', role: 'Lead Engineer' },
  { id: '4', name: 'Lillie Bryant', role: 'Head of Design' },
];

const stats = [
  { label: 'Active Users', value: '50,917', icon: 'users' },
  { label: 'Athletes Listed', value: '5,678', icon: 'athletes' },
  { label: 'Volume Traded', value: '$60,309,502', icon: 'money' },
  { label: 'Daily Trades', value: '125,000+', icon: 'trades' },
];

export function SpAboutPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/30 via-slate-900 to-cyan-900/20" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-violet-600/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8">
            <Link to="/spovest" className="hover:text-white transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white">About Us</span>
          </nav>

          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              A Few Words{' '}
              <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                About Us
              </span>
            </h1>
            <p className="text-xl text-slate-300">
              Love and passion for the game. That's what drives us to create the best fantasy sports trading platform in the world.
            </p>
          </div>
        </div>
      </section>

      {/* Mission */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-6">
                A Sports Trading Experience Like{' '}
                <span className="text-violet-400">Never Before</span>
              </h2>
              <p className="text-slate-300 mb-6 leading-relaxed">
                Spovest is a fantasy sports stock exchange where you can buy and sell shares of professional athletes as if they were stocks. Our platform combines the excitement of fantasy sports with the strategy of stock trading.
              </p>
              <p className="text-slate-300 mb-6 leading-relaxed">
                Founded in 2020, we've grown from a small startup to a platform trusted by over 50,000 traders worldwide. Our mission is to make fantasy sports more engaging, strategic, and rewarding for everyone.
              </p>
              <p className="text-slate-300 leading-relaxed">
                Whether you're a casual fan or a seasoned trader, Spovest offers a unique way to engage with your favorite sports and athletes while building real value.
              </p>
            </div>

            {/* Image placeholder */}
            <div className="bg-gradient-to-br from-violet-600/20 to-cyan-600/20 rounded-2xl aspect-video flex items-center justify-center border border-slate-700/50">
              <div className="text-center">
                <svg className="w-24 h-24 text-violet-400/50 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <p className="text-slate-500">Platform Overview Video</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat) => (
              <SpCard key={stat.label} variant="gradient" className="text-center">
                <p className="text-3xl sm:text-4xl font-bold text-white mb-2">{stat.value}</p>
                <p className="text-sm text-slate-400">{stat.label}</p>
              </SpCard>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Our Core Values</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              The principles that guide everything we do at Spovest.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Transparency',
                description: 'Clear pricing, fair markets, and honest communication. You always know exactly what you are trading and why.',
                icon: (
                  <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                ),
              },
              {
                title: 'Innovation',
                description: 'Constantly pushing boundaries to create new features and experiences that enhance your trading journey.',
                icon: (
                  <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                ),
              },
              {
                title: 'Community',
                description: 'Building a vibrant community of sports fans and traders who share insights and celebrate victories together.',
                icon: (
                  <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                ),
              },
            ].map((value) => (
              <SpCard key={value.title} variant="bordered" hover className="text-center">
                <div className="text-violet-400 mb-4 flex justify-center">{value.icon}</div>
                <h3 className="text-xl font-bold text-white mb-3">{value.title}</h3>
                <p className="text-slate-400">{value.description}</p>
              </SpCard>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Meet Our Team</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              The passionate individuals behind Spovest who work tirelessly to bring you the best trading experience.
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {teamMembers.map((member) => (
              <SpTeamMemberCard key={member.id} member={member} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 via-transparent to-cyan-600/20" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Experience the Future of Fantasy Sports
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            Join thousands of traders who are already building their portfolios on Spovest.
          </p>
          <Link to="/spovest/signup">
            <SpButton size="xl" className="shadow-xl shadow-violet-500/30">
              Start Trading Today
            </SpButton>
          </Link>
        </div>
      </section>
    </div>
  );
}
