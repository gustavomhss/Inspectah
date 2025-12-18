import { useState } from 'react';
import { Link } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpButton } from '../components/ui/Button';
import { SpAccordion, SpAccordionItem } from '../components/ui/Accordion';
import type { SpFaqItem } from '../types';

const faqItems: SpFaqItem[] = [
  // General
  {
    id: '1',
    category: 'general',
    question: 'What is Spovest?',
    answer: 'Spovest is a fantasy sports stock exchange where you can buy and sell shares of professional athletes as if they were stocks. Player prices fluctuate based on their real-world performance, allowing you to profit by buying low and selling high.',
  },
  {
    id: '2',
    category: 'general',
    question: 'How do I create an account?',
    answer: 'Creating an account is simple! Click the "Sign Up" button, enter your email and create a password. Verify your email, and you\'re ready to start trading. The whole process takes less than a minute.',
  },
  {
    id: '3',
    category: 'general',
    question: 'Is Spovest available in my country?',
    answer: 'Spovest is currently available in the United States, Canada, and most European countries. We\'re actively working on expanding to more regions. Check our Terms of Service for the complete list of supported countries.',
  },
  {
    id: '4',
    category: 'general',
    question: 'How do I change my username?',
    answer: 'You can change your username in your account settings. Go to Settings > Profile > Edit Username. Note that usernames can only be changed once every 30 days.',
  },
  {
    id: '5',
    category: 'general',
    question: 'How do I reset my password?',
    answer: 'Click "Forgot Password" on the login page, enter your email address, and we\'ll send you a password reset link. The link expires after 24 hours for security reasons.',
  },
  // Trading
  {
    id: '6',
    category: 'trading',
    question: 'What is trading?',
    answer: '"Trading" refers to the buying and selling of shares in athletes. When you buy shares, you\'re investing in that player\'s performance. When they perform well, their price goes up, and you can sell for a profit.',
  },
  {
    id: '7',
    category: 'trading',
    question: 'How are player prices determined?',
    answer: 'Player prices are determined by a combination of factors including recent performance, historical stats, upcoming matchups, injuries, and market demand. Our algorithm updates prices in real-time based on these factors.',
  },
  {
    id: '8',
    category: 'trading',
    question: 'What sports are available?',
    answer: 'We currently support NBA, NFL, MLB, NHL, Soccer (major leagues), Golf (PGA), and ESports. We\'re constantly adding new sports and leagues based on user demand.',
  },
  {
    id: '9',
    category: 'trading',
    question: 'What are trading fees?',
    answer: 'We charge a small 2.5% fee on each transaction to maintain the platform. This fee is automatically calculated and shown before you confirm any trade.',
  },
  {
    id: '10',
    category: 'trading',
    question: 'Can I trade 24/7?',
    answer: 'Yes! Unlike traditional fantasy sports, you can trade on Spovest 24 hours a day, 7 days a week. Player prices update continuously, so there\'s always an opportunity to trade.',
  },
  // Account
  {
    id: '11',
    category: 'account',
    question: 'How do I deposit funds?',
    answer: 'Go to your Portfolio page and click "Deposit". We accept major credit/debit cards, bank transfers, PayPal, and popular cryptocurrencies. Deposits are usually processed within minutes.',
  },
  {
    id: '12',
    category: 'account',
    question: 'How do I withdraw my earnings?',
    answer: 'Navigate to Settings > Withdraw Funds. Select your preferred withdrawal method and enter the amount. Withdrawals typically take 1-3 business days to process.',
  },
  {
    id: '13',
    category: 'account',
    question: 'Is my money safe?',
    answer: 'Absolutely. We use bank-level encryption to protect your data and funds. All user funds are held in segregated accounts and are FDIC insured up to $250,000.',
  },
  {
    id: '14',
    category: 'account',
    question: 'What is the referral program?',
    answer: 'Earn $50 for every friend you refer who makes a deposit. Your friend also gets a free stock worth up to $100. There\'s no limit to how many friends you can refer!',
  },
  {
    id: '15',
    category: 'account',
    question: 'How do I close my account?',
    answer: 'To close your account, first withdraw any remaining balance. Then go to Settings > Account > Close Account. Please note this action is permanent and cannot be undone.',
  },
];

const categories = [
  { id: 'all', label: 'All Questions' },
  { id: 'general', label: 'General' },
  { id: 'trading', label: 'Trading' },
  { id: 'account', label: 'Account' },
];

export function SpFaqPage() {
  const [activeCategory, setActiveCategory] = useState('all');

  const filteredFaqs = activeCategory === 'all'
    ? faqItems
    : faqItems.filter((item) => item.category === activeCategory);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/30 via-slate-900 to-cyan-900/20" />
        <div className="absolute bottom-10 left-20 w-72 h-72 bg-violet-600/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8">
            <Link to="/spovest" className="hover:text-white transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white">FAQ</span>
          </nav>

          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              Frequently Asked{' '}
              <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                Questions
              </span>
            </h1>
            <p className="text-xl text-slate-300">
              Find answers to common questions about Spovest. Can't find what you're looking for?{' '}
              <Link to="/spovest/contact" className="text-violet-400 hover:underline">
                Contact us
              </Link>
              .
            </p>
          </div>
        </div>
      </section>

      {/* FAQ Content */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 mb-10">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={clsx(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  activeCategory === category.id
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                )}
              >
                {category.label}
              </button>
            ))}
          </div>

          {/* FAQ List */}
          <SpAccordion>
            {filteredFaqs.map((item, index) => (
              <SpAccordionItem key={item.id} title={item.question} defaultOpen={index === 0}>
                {item.answer}
              </SpAccordionItem>
            ))}
          </SpAccordion>
        </div>
      </section>

      {/* Still Have Questions */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-br from-violet-600/20 to-cyan-600/20 rounded-2xl p-12 border border-slate-700/50">
            <svg className="w-16 h-16 text-violet-400 mx-auto mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-2xl font-bold text-white mb-4">Still Have Questions?</h2>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">
              Our support team is here to help. Reach out and we'll get back to you within 24 hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/spovest/contact">
                <SpButton size="lg">
                  Contact Support
                </SpButton>
              </Link>
              <a href="mailto:support@spovest.com">
                <SpButton variant="outline" size="lg">
                  Email Us
                </SpButton>
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
