import { useState } from 'react';
import { Link } from 'react-router-dom';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpStatCard } from '../components/ui/Card';
import { SpReferralsTable } from '../components/ui/Table';
import type { SpReferral } from '../types';

const mockReferrals: SpReferral[] = [
  { id: '1', email: 'john***@gmail.com', date: '2024-01-15', level: 1, status: 'active' },
  { id: '2', email: 'sarah***@yahoo.com', date: '2024-01-12', level: 1, status: 'active' },
  { id: '3', email: 'mike***@outlook.com', date: '2024-01-10', level: 1, status: 'pending' },
  { id: '4', email: 'emma***@gmail.com', date: '2024-01-08', level: 2, status: 'active' },
  { id: '5', email: 'chris***@icloud.com', date: '2024-01-05', level: 1, status: 'active' },
];

export function SpAffiliatePage() {
  const [copied, setCopied] = useState(false);
  const referralLink = 'https://www.spovest.com?ref=ardf0u4803';

  const handleCopyLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Affiliate Program</h1>
        <p className="text-slate-400">Refer friends and earn rewards</p>
      </div>

      {/* Hero Banner */}
      <SpCard variant="gradient" className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 via-transparent to-cyan-600/20" />
        <div className="relative text-center py-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-violet-600/20 mb-6">
            <svg className="w-10 h-10 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Refer a Friend</h2>
          <p className="text-5xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent mb-4">
            Earn $50
          </p>
          <p className="text-slate-400 max-w-md mx-auto">
            For every friend who signs up and makes a deposit using your referral link.
            Plus, they get a free stock worth up to $100!
          </p>
        </div>
      </SpCard>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <SpStatCard
          label="Total Earnings"
          value={2956}
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <SpStatCard
          label="This Month"
          value={208.70}
          changePercent={15.2}
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
        />
        <SpStatCard
          label="Total Referrals"
          value="59"
          prefix=""
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
      </div>

      {/* Referral Link */}
      <SpCard variant="bordered">
        <h3 className="text-lg font-bold text-white mb-4">Your Referral Link</h3>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 flex items-center px-4 py-3 bg-slate-800 rounded-lg border border-slate-700">
            <span className="text-slate-300 truncate text-sm">{referralLink}</span>
          </div>
          <SpButton onClick={handleCopyLink}>
            {copied ? (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                Copy Link
              </>
            )}
          </SpButton>
        </div>

        {/* Share Buttons */}
        <div className="mt-6">
          <p className="text-sm text-slate-400 mb-3">Share via:</p>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1877f2] hover:bg-[#166fe5] text-white rounded-lg transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              Facebook
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-black hover:bg-gray-900 text-white rounded-lg transition-colors border border-gray-700">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
              Twitter
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#25D366] hover:bg-[#20bd5a] text-white rounded-lg transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              WhatsApp
            </button>
          </div>
        </div>
      </SpCard>

      {/* How It Works */}
      <SpCard variant="bordered">
        <h3 className="text-lg font-bold text-white mb-6">How It Works</h3>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              step: '1',
              title: 'Share Your Link',
              description: 'Copy your unique referral link and share it with friends, family, or on social media.',
            },
            {
              step: '2',
              title: 'Friend Signs Up',
              description: 'When someone clicks your link and creates an account, they become your referral.',
            },
            {
              step: '3',
              title: 'Earn Rewards',
              description: 'Once they make their first deposit, you earn $50 and they get a free stock!',
            },
          ].map((item) => (
            <div key={item.step} className="text-center">
              <div className="w-12 h-12 rounded-full bg-violet-600/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-violet-400">{item.step}</span>
              </div>
              <h4 className="font-semibold text-white mb-2">{item.title}</h4>
              <p className="text-sm text-slate-400">{item.description}</p>
            </div>
          ))}
        </div>
      </SpCard>

      {/* Referrals Table */}
      <SpCard variant="bordered" padding="none">
        <div className="p-4 border-b border-slate-700/50">
          <h3 className="text-lg font-bold text-white">Your Referrals</h3>
        </div>
        <SpReferralsTable referrals={mockReferrals} />
      </SpCard>

      {/* Terms */}
      <p className="text-sm text-slate-500 text-center">
        By participating in the referral program, you agree to our{' '}
        <Link to="/spovest/terms" className="text-violet-400 hover:underline">
          Terms and Conditions
        </Link>
        . Commission is paid after the referred user makes a minimum deposit of $25.
      </p>
    </div>
  );
}
