import { ReactNode } from 'react';
import { clsx } from 'clsx';

// Generic Table Components
interface TableProps {
  children: ReactNode;
  className?: string;
}

export function SpTable({ children, className }: TableProps) {
  return (
    <div className={clsx('overflow-x-auto rounded-xl border border-slate-700/50', className)}>
      <table className="w-full">{children}</table>
    </div>
  );
}

export function SpTableHead({ children }: { children: ReactNode }) {
  return <thead className="bg-slate-800/50">{children}</thead>;
}

export function SpTableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-slate-700/50">{children}</tbody>;
}

export function SpTableRow({ children, className, onClick }: { children: ReactNode; className?: string; onClick?: () => void }) {
  return (
    <tr
      className={clsx(
        'hover:bg-slate-800/30 transition-colors',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

export function SpTableHeader({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <th className={clsx('px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider', className)}>
      {children}
    </th>
  );
}

export function SpTableCell({ children, className }: { children: ReactNode; className?: string }) {
  return <td className={clsx('px-4 py-4 text-sm text-slate-300', className)}>{children}</td>;
}

// Player Portfolio Table
import type { SpPortfolioItem } from '../../types';

interface PortfolioTableProps {
  items: SpPortfolioItem[];
  onPlayerClick?: (playerId: string) => void;
}

export function SpPortfolioTable({ items, onPlayerClick }: PortfolioTableProps) {
  return (
    <SpTable>
      <SpTableHead>
        <tr>
          <SpTableHeader>Player</SpTableHeader>
          <SpTableHeader className="text-right">Change</SpTableHeader>
          <SpTableHeader className="text-right">Share Price</SpTableHeader>
          <SpTableHeader className="text-right">Bought At</SpTableHeader>
          <SpTableHeader className="text-right">My Shares</SpTableHeader>
          <SpTableHeader className="text-right">Earning</SpTableHeader>
        </tr>
      </SpTableHead>
      <SpTableBody>
        {items.map((item) => {
          const isPositive = item.earning >= 0;
          return (
            <SpTableRow key={item.playerId} onClick={() => onPlayerClick?.(item.playerId)}>
              <SpTableCell>
                <div className="flex items-center gap-3">
                  {item.player.avatar ? (
                    <img src={item.player.avatar} alt={item.player.name} className="w-10 h-10 rounded-full" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-white text-sm font-bold">
                      {item.player.firstName[0]}{item.player.lastName[0]}
                    </div>
                  )}
                  <div>
                    <p className="font-medium text-white">{item.player.name}</p>
                    <p className="text-xs text-slate-500">{item.player.team}</p>
                  </div>
                </div>
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={clsx(isPositive ? 'text-emerald-400' : 'text-red-400')}>
                  {isPositive ? '+' : ''}{item.player.priceChangePercent.toFixed(2)}%
                </span>
              </SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                ${item.player.price.toFixed(2)}
              </SpTableCell>
              <SpTableCell className="text-right">
                ${item.boughtAt.toFixed(2)}
              </SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                {item.shares}
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={clsx('font-medium', isPositive ? 'text-emerald-400' : 'text-red-400')}>
                  {isPositive ? '+' : ''}${item.earning.toFixed(2)}
                </span>
              </SpTableCell>
            </SpTableRow>
          );
        })}
      </SpTableBody>
    </SpTable>
  );
}

// Watchlist Table
import type { SpPlayer } from '../../types';

interface WatchlistTableProps {
  players: SpPlayer[];
  onPlayerClick?: (playerId: string) => void;
  onRemove?: (playerId: string) => void;
}

export function SpWatchlistTable({ players, onPlayerClick, onRemove }: WatchlistTableProps) {
  return (
    <SpTable>
      <SpTableHead>
        <tr>
          <SpTableHeader>Player</SpTableHeader>
          <SpTableHeader className="text-right">Change</SpTableHeader>
          <SpTableHeader className="text-right">Share Price</SpTableHeader>
          <SpTableHeader className="text-right">Team</SpTableHeader>
          {onRemove && <SpTableHeader className="w-12">&nbsp;</SpTableHeader>}
        </tr>
      </SpTableHead>
      <SpTableBody>
        {players.map((player) => {
          const isPositive = player.priceChange >= 0;
          return (
            <SpTableRow key={player.id}>
              <SpTableCell>
                <div
                  className="flex items-center gap-3 cursor-pointer"
                  onClick={() => onPlayerClick?.(player.id)}
                >
                  {player.avatar ? (
                    <img src={player.avatar} alt={player.name} className="w-10 h-10 rounded-full" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center text-white text-sm font-bold">
                      {player.firstName[0]}{player.lastName[0]}
                    </div>
                  )}
                  <p className="font-medium text-white hover:text-violet-400 transition-colors">
                    {player.name}
                  </p>
                </div>
              </SpTableCell>
              <SpTableCell className="text-right">
                <span className={clsx(isPositive ? 'text-emerald-400' : 'text-red-400')}>
                  {isPositive ? '+' : ''}{player.priceChangePercent.toFixed(2)}%
                </span>
              </SpTableCell>
              <SpTableCell className="text-right font-medium text-white">
                ${player.price.toFixed(2)}
              </SpTableCell>
              <SpTableCell className="text-right text-slate-400">
                {player.team}
              </SpTableCell>
              {onRemove && (
                <SpTableCell>
                  <button
                    onClick={() => onRemove(player.id)}
                    className="p-1 text-slate-500 hover:text-red-400 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </SpTableCell>
              )}
            </SpTableRow>
          );
        })}
      </SpTableBody>
    </SpTable>
  );
}

// Affiliate Referrals Table
import type { SpReferral } from '../../types';

interface ReferralsTableProps {
  referrals: SpReferral[];
}

export function SpReferralsTable({ referrals }: ReferralsTableProps) {
  return (
    <SpTable>
      <SpTableHead>
        <tr>
          <SpTableHeader>Email</SpTableHeader>
          <SpTableHeader className="text-right">Date</SpTableHeader>
          <SpTableHeader className="text-right">Level</SpTableHeader>
          <SpTableHeader className="text-right">Status</SpTableHeader>
        </tr>
      </SpTableHead>
      <SpTableBody>
        {referrals.map((referral) => (
          <SpTableRow key={referral.id}>
            <SpTableCell className="font-medium text-white">{referral.email}</SpTableCell>
            <SpTableCell className="text-right">
              {new Date(referral.date).toLocaleDateString()}
            </SpTableCell>
            <SpTableCell className="text-right">{referral.level}</SpTableCell>
            <SpTableCell className="text-right">
              <span
                className={clsx(
                  'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                  referral.status === 'active'
                    ? 'bg-emerald-400/10 text-emerald-400'
                    : 'bg-yellow-400/10 text-yellow-400'
                )}
              >
                {referral.status}
              </span>
            </SpTableCell>
          </SpTableRow>
        ))}
      </SpTableBody>
    </SpTable>
  );
}

// Game History Table
interface GameHistoryRow {
  date: string;
  opponent: string;
  points: number;
  assists: number;
  rebounds: number;
  steals: number;
  minutes: number;
  fantasyPoints: number;
}

interface GameHistoryTableProps {
  games: GameHistoryRow[];
}

export function SpGameHistoryTable({ games }: GameHistoryTableProps) {
  return (
    <SpTable>
      <SpTableHead>
        <tr>
          <SpTableHeader>Date</SpTableHeader>
          <SpTableHeader>Opponent</SpTableHeader>
          <SpTableHeader className="text-right">PTS</SpTableHeader>
          <SpTableHeader className="text-right">AST</SpTableHeader>
          <SpTableHeader className="text-right">REB</SpTableHeader>
          <SpTableHeader className="text-right">STL</SpTableHeader>
          <SpTableHeader className="text-right">MIN</SpTableHeader>
          <SpTableHeader className="text-right">FTPS</SpTableHeader>
        </tr>
      </SpTableHead>
      <SpTableBody>
        {games.map((game, index) => (
          <SpTableRow key={index}>
            <SpTableCell>{game.date}</SpTableCell>
            <SpTableCell>{game.opponent}</SpTableCell>
            <SpTableCell className="text-right font-medium text-white">{game.points}</SpTableCell>
            <SpTableCell className="text-right">{game.assists}</SpTableCell>
            <SpTableCell className="text-right">{game.rebounds}</SpTableCell>
            <SpTableCell className="text-right">{game.steals}</SpTableCell>
            <SpTableCell className="text-right">{game.minutes}</SpTableCell>
            <SpTableCell className="text-right font-medium text-violet-400">{game.fantasyPoints}</SpTableCell>
          </SpTableRow>
        ))}
      </SpTableBody>
    </SpTable>
  );
}
