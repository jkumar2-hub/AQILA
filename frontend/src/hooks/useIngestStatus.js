// useIngestStatus — polls GET /api/ingest/status/{sourceId} every 1 second.
// Stops automatically when status reaches 'indexed' or 'failed'.
// Library: TanStack Query v5
// Reference: docs/API_CONTRACTS.md §API Endpoints

import { useQuery } from '@tanstack/react-query'
import { fetchIngestStatusFn } from '../lib/uploadService'

/**
 * Poll the ingest status endpoint for a given source.
 *
 * @param {string|null} sourceId  - the source_id returned by POST /api/ingest/upload
 * @param {boolean}     enabled   - set to false to disable (e.g. not yet processing)
 *
 * @returns TanStack Query result — { data: { status } | undefined, isError, error }
 */
export function useIngestStatus(sourceId, enabled = true) {
  return useQuery({
    queryKey: ['ingestStatus', sourceId],
    queryFn: () => fetchIngestStatusFn(sourceId),

    // Only poll when enabled and we have a sourceId to poll
    enabled: enabled && Boolean(sourceId),

    // Poll every 1 second; stop automatically on terminal states
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'indexed' || status === 'failed') return false
      return 1000
    },

    // Do not auto-retry failed fetches — surface errors immediately
    retry: false,

    // Always treat data as stale so each refetch goes to the network
    staleTime: 0,
  })
}
