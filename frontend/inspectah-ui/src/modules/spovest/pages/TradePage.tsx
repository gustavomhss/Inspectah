import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { clsx } from 'clsx';
import { SpButton } from '../components/ui/Button';
import { SpCard, SpPlayerCard } from '../components/ui/Card';
import { SpInput, SpNumberInput } from '../components/ui/Input';
import { SpBadge, SpSportBadge, SpPriceChangeBadge } from '../components/ui/Badge';
import type { SpPlayer, SpSport, SpGame } from '../types';

// Mock data
const allPlayers: SpPlayer[] = [
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
  {
    id: '6',
    name: 'Jayson Tatum',
    firstName: 'Jayson',
    lastName: 'Tatum',
    team: 'Boston Celtics',
    position: 'SF',
    sport: 'NBA',
    price: 1.28,
    priceChange: 0.05,
    priceChangePercent: 4.1,
    stats: { games: 1, points: 26.2, assists: 4.3, rebounds: 8.1, steals: 1.0, minutes: 35.5, fantasyPoints: 38.4 },
  },
];

const sports: SpSport[] = ['NBA', 'NFL', 'MLB', 'NHL', 'Soccer', 'Golf', 'ESports'];

const upcomingGames: SpGame[] = [
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
];

export function SpTradePage() {
  const { sport } = useParams<{ sport?: string }>();
  const [selectedPlayer, setSelectedPlayer] = useState<SpPlayer | null>(null);
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [shares, setShares] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');

  const activeSport = (sport?.toUpperCase() as SpSport) || 'NBA';

  const filteredPlayers = allPlayers.filter((player) => {
    const matchesSport = player.sport === activeSport;
    const matchesSearch = player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      player.team.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSport && matchesSearch;
  });

  const fee = selectedPlayer ? (selectedPlayer.price * shares * 0.025) : 0;
  const total = selectedPlayer ? (selectedPlayer.price * shares + fee) : 0;

  const handleTrade = () => {
    console.log('Trade:', { player: selectedPlayer, type: tradeType, shares, total });
    // Reset form
    setSelectedPlayer(null);
    setShares(1);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Trade</h1>
          <p className="text-slate-400">Buy and sell athlete shares</p>
        </div>
      </div>

      {/* Sport Tabs */}
      <div className="flex flex-wrap gap-2 mb-8">
        {sports.map((s) => (
          <Link
            key={s}
            to={`/spovest/trade/${s.toLowerCase()}`}
            className={clsx(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              s === activeSport
                ? 'bg-violet-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
            )}
          >
            {s}
          </Link>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Players List */}
        <div className="lg:col-span-2 space-y-6">
          {/* Search */}
          <SpInput
            placeholder="Search players..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />

          {/* Players Grid */}
          <div className="grid sm:grid-cols-2 gap-6">
            {filteredPlayers.map((player) => (
              <SpPlayerCard
                key={player.id}
                player={player}
                onClick={() => setSelectedPlayer(player)}
                showActions={false}
              />
            ))}
          </div>

          {filteredPlayers.length === 0 && (
            <div className="text-center py-12">
              <p className="text-slate-400">No players found matching your search.</p>
            </div>
          )}
        </div>

        {/* Trade Panel */}
        <div className="space-y-6">
          {/* Selected Player / Trade Form */}
          {selectedPlayer ? (
            <SpCard variant="gradient">
              {/* Player Info */}
              <div className="flex items-start gap-4 mb-6">
                <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-violet-600/20 to-cyan-600/20 flex items-center justify-center text-2xl text-white font-bold">
                  {selectedPlayer.firstName[0]}{selectedPlayer.lastName[0]}
                </div>
                <div className="flex-1">
                  <p className="text-xs text-violet-400 uppercase tracking-wide">{selectedPlayer.team}</p>
                  <h3 className="text-lg font-bold text-white">{selectedPlayer.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xl font-bold text-white">${selectedPlayer.price.toFixed(2)}</span>
                    <SpPriceChangeBadge change={selectedPlayer.priceChange} changePercent={selectedPlayer.priceChangePercent} size="sm" />
                  </div>
                </div>
              </div>

              {/* Trade Type Toggle */}
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
                  Buy Shares
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
                  Sell Shares
                </button>
              </div>

              {/* Shares Input */}
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
                  <span className="text-slate-400">Share Price</span>
                  <span className="text-white">${selectedPlayer.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Shares</span>
                  <span className="text-white">x {shares}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Subtotal</span>
                  <span className="text-white">${(selectedPlayer.price * shares).toFixed(2)}</span>
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

              {/* Trade Button */}
              <SpButton
                onClick={handleTrade}
                variant={tradeType === 'buy' ? 'success' : 'danger'}
                size="lg"
                fullWidth
                className="mt-6"
              >
                {tradeType === 'buy' ? 'Buy' : 'Sell'} {shares} Share{shares > 1 ? 's' : ''} Now
              </SpButton>

              {/* Close */}
              <button
                onClick={() => setSelectedPlayer(null)}
                className="w-full mt-3 text-sm text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
            </SpCard>
          ) : (
            <SpCard variant="bordered" className="text-center py-12">
              <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              <h3 className="text-lg font-semibold text-white mb-2">Select a Player</h3>
              <p className="text-slate-400 text-sm">Click on a player card to start trading</p>
            </SpCard>
          )}

          {/* Upcoming Games */}
          <SpCard variant="bordered">
            <h3 className="font-bold text-white mb-4">Upcoming Games</h3>
            <div className="space-y-3">
              {upcomingGames.map((game) => (
                <div key={game.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <SpSportBadge sport={game.sport} size="sm" />
                    <div className="text-sm">
                      <span className="text-white font-medium">{game.awayTeam.shortName}</span>
                      <span className="text-slate-500 mx-2">@</span>
                      <span className="text-white font-medium">{game.homeTeam.shortName}</span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">
                    {new Date(game.dateTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              ))}
            </div>
            <Link to="/spovest/games" className="block mt-4 text-sm text-violet-400 hover:text-violet-300 text-center">
              View All Games
            </Link>
          </SpCard>
        </div>
      </div>
    </div>
  );
}
