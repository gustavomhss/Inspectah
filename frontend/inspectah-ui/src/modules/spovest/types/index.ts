// Spovest Types - Fantasy Sports Stock Exchange

// ===== Theme =====
export type SpTheme = 'light' | 'dark';

// ===== User =====
export interface SpUser {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  balance: number;
  portfolioValue: number;
  earnings: number;
  followers: number;
  following: number;
  createdAt: string;
}

// ===== Player/Athlete =====
export interface SpPlayer {
  id: string;
  name: string;
  firstName: string;
  lastName: string;
  team: string;
  teamLogo?: string;
  position: string;
  sport: SpSport;
  avatar?: string;
  price: number;
  priceChange: number;
  priceChangePercent: number;
  stats: SpPlayerStats;
}

export interface SpPlayerStats {
  games: number;
  points: number;
  assists: number;
  rebounds: number;
  steals: number;
  minutes: number;
  fantasyPoints: number;
}

export type SpSport = 'NBA' | 'NFL' | 'MLB' | 'NHL' | 'Soccer' | 'Golf' | 'ESports';

// ===== Portfolio =====
export interface SpPortfolioItem {
  playerId: string;
  player: SpPlayer;
  shares: number;
  boughtAt: number;
  currentValue: number;
  earning: number;
  earningPercent: number;
}

export interface SpPortfolio {
  items: SpPortfolioItem[];
  totalValue: number;
  totalEarnings: number;
  totalEarningsPercent: number;
}

// ===== Watchlist =====
export interface SpWatchlistItem {
  playerId: string;
  player: SpPlayer;
  addedAt: string;
}

// ===== Game/Match =====
export interface SpGame {
  id: string;
  sport: SpSport;
  homeTeam: SpTeam;
  awayTeam: SpTeam;
  dateTime: string;
  status: 'upcoming' | 'live' | 'finished';
  homeScore?: number;
  awayScore?: number;
}

export interface SpTeam {
  id: string;
  name: string;
  shortName: string;
  logo?: string;
  sport: SpSport;
}

// ===== Trade =====
export interface SpTrade {
  id: string;
  playerId: string;
  player: SpPlayer;
  type: 'buy' | 'sell';
  shares: number;
  pricePerShare: number;
  totalAmount: number;
  fee: number;
  feePercent: number;
  createdAt: string;
  status: 'pending' | 'completed' | 'cancelled';
}

export interface SpTradeRequest {
  playerId: string;
  type: 'buy' | 'sell';
  shares: number;
}

// ===== Affiliate =====
export interface SpAffiliateStats {
  referralLink: string;
  totalEarnings: number;
  monthlyEarnings: number;
  totalReferrals: number;
  commissionPerReferral: number;
}

export interface SpReferral {
  id: string;
  email: string;
  date: string;
  level: number;
  status: 'pending' | 'active';
}

// ===== FAQ =====
export interface SpFaqItem {
  id: string;
  question: string;
  answer: string;
  category: 'general' | 'sports' | 'trading' | 'account';
}

// ===== Testimonial =====
export interface SpTestimonial {
  id: string;
  name: string;
  location: string;
  avatar?: string;
  text: string;
  rating: number;
}

// ===== Team Member =====
export interface SpTeamMember {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  bio?: string;
}

// ===== Contact Form =====
export interface SpContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
  acceptMarketing: boolean;
}

// ===== Auth =====
export interface SpLoginForm {
  email: string;
  password: string;
}

export interface SpSignupForm {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface SpAuthResponse {
  user: SpUser;
  token: string;
}

// ===== Navigation =====
export interface SpNavItem {
  label: string;
  href: string;
  icon?: string;
  children?: SpNavItem[];
  badge?: string | number;
}

// ===== Stats Card =====
export interface SpStatCard {
  label: string;
  value: string | number;
  change?: number;
  changePercent?: number;
  icon?: string;
}

// ===== Price Trend =====
export interface SpPriceTrend {
  timestamp: string;
  price: number;
}

// ===== Notification =====
export interface SpNotification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
}
