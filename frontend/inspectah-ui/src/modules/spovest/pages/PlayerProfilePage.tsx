import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpStatCard } from '../components/ui/Card';
import { SpNumberInput } from '../components/ui/Input';
import { SpGameHistoryTable } from '../components/ui/Table';
import { SpPriceChangeBadge, SpSportBadge } from '../components/ui/Badge';
import { clsx } from 'clsx';
import type { SpPlayer } from '../types';

// Mock player data
const mockPlayer: SpPlayer = {
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
};

const gameHistory = [
  { date: 'Dec 15', opponent: 'vs LAL', points: 32, assists: 8, rebounds: 5, steals: 2, minutes: 36, fantasyPoints: 48.5 },
  { date: 'Dec 13', opponent: '@ DEN', points: 28, assists: 6, rebounds: 4, steals: 1, minutes: 34, fantasyPoints: 42.2 },
  { date: 'Dec 11', opponent: 'vs PHX', points: 24, assists: 10, rebounds: 3, steals: 2, minutes: 32, fantasyPoints: 39.8 },
  { date: 'Dec 9', opponent: '@ SAC', points: 36, assists: 5, rebounds: 6, steals: 1, minutes: 38, fantasyPoints: 51.2 },
  { date: 'Dec 7', opponent: 'vs BOS', points: 22, assists: 7, rebounds: 4, steals: 3, minutes: 35, fantasyPoints: 38.6 },
];

const priceHistory = [65, 70, 68, 75, 72, 80, 78, 85, 82, 90, 88, 95, 92, 100, 106];

export function SpPlayerProfilePage() {
  const { playerId } = useParams<{ playerId: string }>();
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [shares, setShares] = useState(1);
  const [activeTab, setActiveTab] = useState<'stats' | 'trends' | 'games'>('stats');

  // In real app, fetch player by ID
  const player = mockPlayer;

  const fee = player.price * shares * 0.025;
  const total = player.price * shares + (tradeType === 'buy' ? fee : -fee);

  const handleTrade = () => {
    console.log('Trade:', { player, type: tradeType, shares, total });
  };

  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-slate-400 mb-6">
        <Link to="/spovest/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
        <span>/</span>
        <Link to="/spovest/trade" className="hover:text-white transition-colors">Trade</Link>
        <span>/</span>
        <span className="text-white">{player.name}</span>
      </nav>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Player Header */}
          <SpCard variant="gradient">
            <div className="flex flex-col sm:flex-row items-start gap-6">
              {/* Avatar */}
              <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-violet-600/30 to-cyan-600/30 flex items-center justify-center text-5xl text-white font-bold">
                {player.firstName[0]}{player.lastName[0]}
              </div>

              {/* Info */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <SpSportBadge sport={player.sport} />
                  <span className="text-slate-400 text-sm">{player.position}</span>
                </div>
                <h1 className="text-3xl font-bold text-white mb-1">{player.name}</h1>
                <p className="text-violet-400 mb-4">{player.team}</p>

                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-3xl font-bold text-white">${player.price.toFixed(2)}</p>
                    <p className="text-sm text-slate-400">Current Price</p>
                  </div>
                  <SpPriceChangeBadge
                    change={player.priceChange}
                    changePercent={player.priceChangePercent}
                    size="lg"
                  />
                </div>
              </div>
            </div>
          </SpCard>

          {/* Stats Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Games', value: player.stats.games.toFixed(1) },
              { label: 'Points', value: player.stats.points.toFixed(1) },
              { label: 'Assists', value: player.stats.assists.toFixed(1) },
              { label: 'Rebounds', value: player.stats.rebounds.toFixed(1) },
              { label: 'Steals', value: player.stats.steals.toFixed(1) },
              { label: 'Minutes', value: player.stats.minutes.toFixed(1) },
              { label: 'Fantasy Pts', value: player.stats.fantasyPoints.toFixed(1) },
            ].map((stat) => (
              <SpCard key={stat.label} variant="bordered" className="text-center">
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-xs text-slate-400">{stat.label}</p>
              </SpCard>
            ))}
          </div>

          {/* Tabs */}
          <div className="border-b border-slate-700/50">
            <div className="flex gap-1">
              {[
                { id: 'stats', label: 'Statistics' },
                { id: 'trends', label: 'Price Trends' },
                { id: 'games', label: 'Game History' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={clsx(
                    'px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
                    activeTab === tab.id
                      ? 'text-white border-violet-500'
                      : 'text-slate-400 border-transparent hover:text-white'
                  )}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'stats' && (
            <SpCard variant="bordered">
              <h3 className="text-lg font-bold text-white mb-4">Next Game Projections</h3>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
                {[
                  { label: 'Points', value: '28.5', change: '+2.3' },
                  { label: 'Assists', value: '7.2', change: '+0.8' },
                  { label: 'Rebounds', value: '4.8', change: '+0.4' },
                  { label: 'Steals', value: '1.8', change: '+0.2' },
                  { label: 'Minutes', value: '35.0', change: '+1.5' },
                  { label: 'Fantasy', value: '45.2', change: '+4.1' },
                ].map((proj) => (
                  <div key={proj.label} className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-xl font-bold text-white">{proj.value}</p>
                    <p className="text-emerald-400 text-xs">{proj.change}</p>
                    <p className="text-xs text-slate-500 mt-1">{proj.label}</p>
                  </div>
                ))}
              </div>
            </SpCard>
          )}

          {activeTab === 'trends' && (
            <SpCard variant="bordered">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white">Price History</h3>
                <div className="flex gap-2">
                  {['1D', '1W', '1M', '3M'].map((period) => (
                    <button
                      key={period}
                      className="px-3 py-1 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>
              {/* Simple Chart */}
              <div className="h-64 flex items-end justify-between gap-1">
                {priceHistory.map((price, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-violet-600/50 to-cyan-600/50 rounded-t hover:from-violet-500/60 hover:to-cyan-500/60 transition-colors cursor-pointer"
                    style={{ height: `${price}%` }}
                    title={`$${(price / 100).toFixed(2)}`}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-4 text-xs text-slate-500">
                <span>2 weeks ago</span>
                <span>1 week ago</span>
                <span>Now</span>
              </div>
            </SpCard>
          )}

          {activeTab === 'games' && (
            <SpGameHistoryTable games={gameHistory} />
          )}
        </div>

        {/* Trade Panel */}
        <div className="space-y-6">
          <SpCard variant="gradient">
            <h3 className="text-lg font-bold text-white mb-4">Trade {player.firstName}</h3>

            {/* Holdings */}
            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg mb-6">
              <div>
                <p className="text-sm text-slate-400">Your Holdings</p>
                <p className="text-xl font-bold text-white">0 Shares</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-400">Value</p>
                <p className="text-xl font-bold text-white">$0.00</p>
              </div>
            </div>

            {/* Trade Type */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setTradeType('buy')}
                className={clsx(
                  'flex-1 py-3 rounded-lg font-semibold transition-colors',
                  tradeType === 'buy'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                )}
              >
                Buy
              </button>
              <button
                onClick={() => setTradeType('sell')}
                className={clsx(
                  'flex-1 py-3 rounded-lg font-semibold transition-colors',
                  tradeType === 'sell'
                    ? 'bg-red-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                )}
              >
                Sell
              </button>
            </div>

            {/* Shares */}
            <SpNumberInput
              label="Amount of Shares"
              value={shares}
              onChange={setShares}
              min={1}
              max={1000}
            />

            {/* Summary */}
            <div className="mt-6 space-y-3 p-4 bg-slate-800/50 rounded-lg">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Price per Share</span>
                <span className="text-white">${player.price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Shares</span>
                <span className="text-white">x {shares}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Subtotal</span>
                <span className="text-white">${(player.price * shares).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Fee (2.5%)</span>
                <span className="text-white">${fee.toFixed(2)}</span>
              </div>
              <div className="border-t border-slate-700 pt-3 flex justify-between">
                <span className="font-semibold text-white">Total</span>
                <span className="font-bold text-lg text-white">${total.toFixed(2)}</span>
              </div>
            </div>

            <SpButton
              onClick={handleTrade}
              variant={tradeType === 'buy' ? 'success' : 'danger'}
              size="lg"
              fullWidth
              className="mt-6"
            >
              {tradeType === 'buy' ? 'Buy' : 'Sell'} {shares} Share{shares > 1 ? 's' : ''} Now
            </SpButton>
          </SpCard>

          {/* Add to Watchlist */}
          <SpButton variant="outline" fullWidth>
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Add to Watchlist
          </SpButton>
        </div>
      </div>
    </div>
  );
}
