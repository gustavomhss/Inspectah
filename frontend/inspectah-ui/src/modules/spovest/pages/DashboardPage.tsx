import { Link } from 'react-router-dom';
import { SpStatCard, SpCard } from '../components/ui/Card';
import { SpPortfolioTable, SpWatchlistTable } from '../components/ui/Table';
import { SpButton } from '../components/ui/Button';
import type { SpPortfolioItem, SpPlayer, SpGame } from '../types';

// Mock data
const mockPortfolioItems: SpPortfolioItem[] = [
  {
    playerId: '1',
    player: {
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
    shares: 50,
    boughtAt: 0.95,
    currentValue: 53.0,
    earning: 5.5,
    earningPercent: 11.58,
  },
  {
    playerId: '2',
    player: {
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
    shares: 30,
    boughtAt: 1.10,
    currentValue: 37.5,
    earning: 4.5,
    earningPercent: 13.64,
  },
  {
    playerId: '3',
    player: {
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
    shares: 20,
    boughtAt: 1.22,
    currentValue: 23.6,
    earning: -0.8,
    earningPercent: -3.28,
  },
];

const mockWatchlist: SpPlayer[] = [
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
  {
    id: '5',
    name: 'Luka Doncic',
    firstName: 'Luka',
    lastName: 'Doncic',
    team: 'Dallas Mavericks',
    position: 'PG',
    sport: 'NBA',
    price: 1.35,
    priceChange: 0.18,
    priceChangePercent: 15.4,
    stats: { games: 1, points: 32.1, assists: 8.4, rebounds: 9.1, steals: 1.3, minutes: 36.8, fantasyPoints: 48.2 },
  },
];

const mockUpcomingGames: SpGame[] = [
  {
    id: '1',
    sport: 'NBA',
    homeTeam: { id: '1', name: 'Los Angeles Lakers', shortName: 'LAL', sport: 'NBA' },
    awayTeam: { id: '2', name: 'Golden State Warriors', shortName: 'GSW', sport: 'NBA' },
    dateTime: new Date(Date.now() + 3600000).toISOString(),
    status: 'upcoming',
  },
  {
    id: '2',
    sport: 'NBA',
    homeTeam: { id: '3', name: 'Milwaukee Bucks', shortName: 'MIL', sport: 'NBA' },
    awayTeam: { id: '4', name: 'Boston Celtics', shortName: 'BOS', sport: 'NBA' },
    dateTime: new Date(Date.now() + 7200000).toISOString(),
    status: 'upcoming',
  },
  {
    id: '3',
    sport: 'NBA',
    homeTeam: { id: '5', name: 'Phoenix Suns', shortName: 'PHX', sport: 'NBA' },
    awayTeam: { id: '6', name: 'Denver Nuggets', shortName: 'DEN', sport: 'NBA' },
    dateTime: new Date(Date.now() + 10800000).toISOString(),
    status: 'upcoming',
  },
];

export function SpDashboardPage() {
  const portfolioValue = mockPortfolioItems.reduce((sum, item) => sum + item.currentValue, 0);
  const totalEarnings = mockPortfolioItems.reduce((sum, item) => sum + item.earning, 0);
  const balance = 500.0;

  const handlePlayerClick = (playerId: string) => {
    console.log('Navigate to player:', playerId);
  };

  const handleRemoveFromWatchlist = (playerId: string) => {
    console.log('Remove from watchlist:', playerId);
  };

  return (
    <div className="p-6 space-y-8">
      {/* Welcome */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">My Portfolio</h1>
          <p className="text-slate-400">Track your investments and earnings</p>
        </div>
        <Link to="/spovest/trade">
          <SpButton>
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Trade
          </SpButton>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <SpStatCard
          label="Portfolio Value"
          value={portfolioValue}
          changePercent={9.84}
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
        />
        <SpStatCard
          label="Account Balance"
          value={balance}
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <SpStatCard
          label="Total Earnings"
          value={totalEarnings}
          changePercent={9.84}
          icon={
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Portfolio Table */}
        <div className="lg:col-span-2">
          <SpCard variant="bordered" padding="none">
            <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
              <h2 className="text-lg font-bold text-white">My Players</h2>
              <Link to="/spovest/trade" className="text-sm text-violet-400 hover:text-violet-300">
                View All
              </Link>
            </div>
            <SpPortfolioTable items={mockPortfolioItems} onPlayerClick={handlePlayerClick} />
          </SpCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Upcoming Games */}
          <SpCard variant="bordered">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-white">Upcoming Games</h3>
              <Link to="/spovest/games" className="text-sm text-violet-400 hover:text-violet-300">
                View All
              </Link>
            </div>
            <div className="space-y-4">
              {mockUpcomingGames.map((game) => (
                <div key={game.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="text-center">
                      <p className="text-sm font-medium text-white">{game.awayTeam.shortName}</p>
                      <p className="text-xs text-slate-500">@</p>
                      <p className="text-sm font-medium text-white">{game.homeTeam.shortName}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400">
                      {new Date(game.dateTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(game.dateTime).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </SpCard>

          {/* Quick Actions */}
          <SpCard variant="gradient">
            <h3 className="font-bold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link to="/spovest/deposit" className="block">
                <SpButton variant="outline" fullWidth>
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Deposit Funds
                </SpButton>
              </Link>
              <Link to="/spovest/withdraw" className="block">
                <SpButton variant="ghost" fullWidth>
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
                  </svg>
                  Withdraw
                </SpButton>
              </Link>
            </div>
          </SpCard>
        </div>
      </div>

      {/* Watchlist */}
      <SpCard variant="bordered" padding="none">
        <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Watchlist</h2>
          <SpButton variant="ghost" size="sm">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Player
          </SpButton>
        </div>
        <SpWatchlistTable
          players={mockWatchlist}
          onPlayerClick={handlePlayerClick}
          onRemove={handleRemoveFromWatchlist}
        />
      </SpCard>
    </div>
  );
}
