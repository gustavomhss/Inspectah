/**
 * S38: Sources Module - Console Fontes v1
 */

// Pages
export { default as SourcesPage } from './pages/SourcesPage';
export { default as SourceDetailPage } from './pages/SourceDetailPage';

// Components
export { default as SourceCard } from './components/SourceCard';
export { default as SourceMetrics } from './components/SourceMetrics';
export { default as IngestionHistory } from './components/IngestionHistory';

// Hooks
export { useSources, useSourceDetail } from './hooks/useSources';
export { useSourceDryRun } from './hooks/useSourceDryRun';

// API
export * from './api/sourcesApi';

// Types
export type * from './types';
