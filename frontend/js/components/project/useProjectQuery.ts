import { useEffect, useState } from "react";

import { QueriesService, Query, QueryResultData } from "api";

export const useProjectQuery = (queryId?: number) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isLoading, setIsLoading] = useState(false);
  const [loadingError, setLoadingError] = useState<Error | null>();

  useEffect(() => {
    const fetchQuery = async () => {
      if (!queryId) {
        setQuery(undefined);
        setQueryResult(undefined);
        return;
      }
      setIsLoading(true);
      try {
        const result = await QueriesService.queriesRetrieve({ id: queryId });
        setQuery(result);
        setLoadingError(null);
      } catch (err) {
        if (err instanceof Error) {
          setLoadingError(err);
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuery();
  }, [queryId]);

  const updateText = async (value: string) => {
    if (!queryId) return;
    const result = await QueriesService.queriesPartialUpdate({
      id: queryId,
      requestBody: { text: value },
    });
    setQuery(result);
  };

  return {
    query,
    setQuery,
    queryResult,
    setQueryResult,
    isLoading,
    loadingError,
    updateText,
  };
};
