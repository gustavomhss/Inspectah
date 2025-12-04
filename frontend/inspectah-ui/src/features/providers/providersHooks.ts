import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '@/app/providers/AuthProvider';
import { useLogger } from '@/app/providers/LoggerProvider';
import {
  fetchProfileDetail,
  fetchProviderDetail,
  fetchProviders,
  fetchProfiles,
  runProfile,
  saveProfile,
  saveProvider,
} from './providersApi';
import type { IngestionProfile, ProfileDetail, ProfileMetrics, ProfileRun, Provider, ProviderDetail } from './providersTypes';

export function useProvidersList() {
  const { token } = useAuth();
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProviders({}, token || undefined);
      setProviders(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { providers, loading, error, reload };
}

export function useProviderDetail(providerId: string | null) {
  const { token } = useAuth();
  const [detail, setDetail] = useState<ProviderDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!providerId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProviderDetail(providerId, token || undefined);
      setDetail(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [providerId, token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { detail, loading, error, setDetail, reload };
}

export function useProfiles(providerId?: string) {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState<IngestionProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!providerId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProfiles({ provider_id: providerId }, token || undefined);
      setProfiles(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [providerId, token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { profiles, loading, error, reload };
}

export function useProfileDetail(profileId: string | null) {
  const { token } = useAuth();
  const [detail, setDetail] = useState<ProfileDetail | null>(null);
  const [runs, setRuns] = useState<ProfileRun[]>([]);
  const [metrics, setMetrics] = useState<ProfileMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProfileDetail(profileId, token || undefined);
      setDetail(data);
      setRuns(data.runs || []);
      setMetrics(data.metrics || null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [profileId, token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { detail, runs, metrics, loading, error, reload, setRuns, setMetrics };
}

export function useSaveProvider(onSaved?: (provider: Provider, isNew?: boolean) => void) {
  const { token, user } = useAuth();
  const { logEvent } = useLogger();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const save = useCallback(
    async (provider: Provider, isNew = false) => {
      setSaving(true);
      setError(null);
      const payload = {
        ...provider,
        created_by: provider?.['created_by'] || user?.id || user?.email || 'admin-ui',
        updated_by: user?.id || user?.email || 'admin-ui',
      } as Provider;
      try {
        const result = await saveProvider(payload, token || undefined, { isNew });
        logEvent('admin.providers.saved', { provider_id: result.id });
        onSaved?.(result, isNew);
        return result;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [token, user, logEvent, onSaved],
  );

  return { save, saving, error, setError };
}

export function useSaveProfile(onSaved?: (profile: IngestionProfile, isNew?: boolean) => void) {
  const { token, user } = useAuth();
  const { logEvent } = useLogger();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const save = useCallback(
    async (profile: IngestionProfile, isNew = false) => {
      setSaving(true);
      setError(null);
      const payload = {
        ...profile,
        created_by: profile?.['created_by'] || user?.id || user?.email || 'admin-ui',
        updated_by: user?.id || user?.email || 'admin-ui',
      } as IngestionProfile;
      try {
        const result = await saveProfile(payload, token || undefined, { isNew });
        logEvent('admin.profiles.saved', { profile_id: result.id, provider_id: result.provider_id });
        onSaved?.(result, isNew);
        return result;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [token, user, logEvent, onSaved],
  );

  return { save, saving, error, setError };
}

export function useRunProfile(onFinished?: (run: ProfileRun) => void) {
  const { token } = useAuth();
  const { logEvent } = useLogger();
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (profileId: string, limit = 3) => {
      setRunning(true);
      setError(null);
      try {
        const result = await runProfile(profileId, token || undefined, limit);
        logEvent('admin.profiles.run_now', { profile_id: profileId, items: result.run?.items });
        onFinished?.(result.run);
        return result.run;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setRunning(false);
      }
    },
    [token, logEvent, onFinished],
  );

  return { run, running, error, setError };
}

export function useProfileHealth(runs: ProfileRun[], metrics?: ProfileMetrics | null) {
  return useMemo(() => {
    const last = runs[runs.length - 1];
    const status = last?.status === 'success' ? 'healthy' : last ? 'degraded' : 'unknown';
    return {
      status,
      lastRun: last?.finished_at,
      totalRuns: metrics?.total_runs || runs.length,
    };
  }, [runs, metrics]);
}
