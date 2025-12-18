/**
 * S39-FE-WS: WebSocket Types
 *
 * Type definitions for WebSocket communication.
 */

export type WSMessageType =
  | 'signal_update'
  | 'notification'
  | 'ingestion_status'
  | 'claim_update'
  | 'flow_status'
  | 'heartbeat'
  | 'error';

export interface WSMessage<T = unknown> {
  type: WSMessageType;
  payload: T;
  timestamp: string;
  id?: string;
}

export interface SignalUpdatePayload {
  signal_id: string;
  signal_type: string;
  value: number;
  scope: string;
  delta?: number;
}

export interface NotificationPayload {
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  source?: string;
}

export interface IngestionStatusPayload {
  run_id: string;
  source_id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress?: number;
  error?: string;
}

export interface ClaimUpdatePayload {
  claim_id: string;
  action: 'created' | 'updated' | 'verified' | 'debunked';
  verdict?: string;
}

export interface FlowStatusPayload {
  flow_id: string;
  execution_id: string;
  status: 'started' | 'completed' | 'failed';
  step?: string;
}

export interface HeartbeatPayload {
  server_time: string;
  clients_connected: number;
}

export type WSEventHandler<T = unknown> = (message: WSMessage<T>) => void;

export interface WSClientConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface WSClientState {
  isConnected: boolean;
  reconnectAttempts: number;
  lastMessageTime: number | null;
}
