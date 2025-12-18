import { Link } from 'react-router-dom';
import { clsx } from 'clsx';

interface FooterProps {
  className?: string;
}

export function SpFooter({ className }: FooterProps) {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={clsx('bg-slate-900 border-t border-slate-700/50', className)}>
      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
          Experience the future of{' '}
          <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
            fantasy sports
          </span>
        </h2>
        <p className="text-slate-400 mb-6 max-w-2xl mx-auto">
          Trade teams like stocks, build your portfolio, and dominate the competition.
        </p>
        <Link
          to="/spovest/signup"
          className={clsx(
            'inline-flex items-center gap-2 px-8 py-3 rounded-lg',
            'bg-gradient-to-r from-violet-600 to-cyan-600',
            'text-white font-semibold text-lg',
            'hover:from-violet-500 hover:to-cyan-500',
            'transition-all duration-200 shadow-lg shadow-violet-500/25'
          )}
        >
          Start Trading
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>

      {/* Main Footer */}
      <div className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="md:col-span-1">
              <Link to="/spovest" className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">S</span>
                </div>
                <span className="text-xl font-bold text-white">Spovest</span>
              </Link>
              <p className="text-sm text-slate-400 mb-4">
                The future of fantasy sports trading. Buy, sell, and trade your favorite athletes like stocks.
              </p>
              {/* App Store Badges */}
              <div className="flex gap-3">
                <a
                  href="#"
                  className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
                >
                  <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
                  </svg>
                  <div className="text-left">
                    <p className="text-[10px] text-slate-400">Download on the</p>
                    <p className="text-sm font-medium text-white">App Store</p>
                  </div>
                </a>
                <a
                  href="#"
                  className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
                >
                  <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 20.5v-17c0-.59.34-1.11.84-1.35L13.69 12l-9.85 9.85c-.5-.25-.84-.76-.84-1.35m13.81-5.38L6.05 21.34l8.49-8.49 2.27 2.27m3.35-4.31c.34.27.59.69.59 1.19s-.22.9-.57 1.18l-2.29 1.32-2.5-2.5 2.5-2.5 2.27 1.31M6.05 2.66l10.76 6.22-2.27 2.27L6.05 2.66z" />
                  </svg>
                  <div className="text-left">
                    <p className="text-[10px] text-slate-400">Get it on</p>
                    <p className="text-sm font-medium text-white">Google Play</p>
                  </div>
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
                Quick Links
              </h3>
              <ul className="space-y-3">
                {['About Us', 'How to Play', 'FAQ', 'Contact'].map((link) => (
                  <li key={link}>
                    <Link
                      to={`/spovest/${link.toLowerCase().replace(/\s+/g, '-')}`}
                      className="text-sm text-slate-400 hover:text-white transition-colors"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Trading */}
            <div>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
                Trading
              </h3>
              <ul className="space-y-3">
                {['NBA', 'NFL', 'MLB', 'NHL', 'Soccer', 'Golf'].map((sport) => (
                  <li key={sport}>
                    <Link
                      to={`/spovest/trade/${sport.toLowerCase()}`}
                      className="text-sm text-slate-400 hover:text-white transition-colors"
                    >
                      {sport}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
                Legal
              </h3>
              <ul className="space-y-3">
                {['Terms of Use', 'Privacy Policy', 'Cookie Policy', 'Responsible Gaming'].map((link) => (
                  <li key={link}>
                    <Link
                      to={`/spovest/${link.toLowerCase().replace(/\s+/g, '-')}`}
                      className="text-sm text-slate-400 hover:text-white transition-colors"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-500">
              &copy; {currentYear} Spovest. All rights reserved.
            </p>
            {/* Social Links */}
            <div className="flex items-center gap-4">
              {[
                { name: 'Twitter', icon: 'M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z' },
                { name: 'Facebook', icon: 'M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z' },
                { name: 'Instagram', icon: 'M16 4H8a4 4 0 00-4 4v8a4 4 0 004 4h8a4 4 0 004-4V8a4 4 0 00-4-4zm2 12a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2h8a2 2 0 012 2v8zm-6-6a3 3 0 100 6 3 3 0 000-6zm4.5-1.5a1 1 0 100-2 1 1 0 000 2z' },
              ].map((social) => (
                <a
                  key={social.name}
                  href="#"
                  className="p-2 text-slate-500 hover:text-white transition-colors"
                  aria-label={social.name}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={social.icon} />
                  </svg>
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
