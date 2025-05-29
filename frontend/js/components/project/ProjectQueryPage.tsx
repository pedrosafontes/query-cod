import { useEffect, useState } from "react";

import { QueriesService, Query, QueryResultData } from "api";

import ExecuteQueryButton from "../query/ExecuteQueryButton";
import QueryEditor from "../query/QueryEditor";
import ErrorAlert from "../query/QueryEditor/ErrorAlert";
import QueryPage from "../query/QueryPage";
import TranspileQueryButton from "../query/TranspileQueryButton";
import { Spinner } from "../ui/spinner";

type ProjectQueryProps = {
  databaseId: number;
  queryId?: number;
  setQueryId: (queryId: number | undefined) => void;
  onTranspile: () => void;
};

const ProjectQueryPage = ({
  databaseId,
  queryId,
  setQueryId,
  onTranspile,
}: ProjectQueryProps) => {
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
      setQuery(undefined);
      setQueryResult(undefined);
      try {
        const result = await QueriesService.queriesRetrieve({
          id: queryId,
        });
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
    if (!queryId) {
      return;
    }

    const result = await QueriesService.queriesPartialUpdate({
      id: queryId,
      requestBody: { text: value },
    });
    setQuery(result);
  };

  const renderHeader = () => {
    const hasErrors = !!query && query.validation_errors.length > 0;
    const actionsDisabled = isLoading || !!loadingError;

    return (
      queryId && (
        <div className="flex justify-between items-center gap-2 mb-5 w-full px-3">
          <h1 className="truncate">{query?.name}</h1>
          <div className="flex gap-2">
            <TranspileQueryButton
              disabled={actionsDisabled}
              hasErrors={hasErrors}
              queryId={queryId}
              setQueryId={setQueryId}
              onSuccess={onTranspile}
            />
            <ExecuteQueryButton
              disabled={actionsDisabled}
              hasErrors={hasErrors}
              queryId={queryId}
              setQueryResult={setQueryResult}
            />
          </div>
        </div>
      )
    );
  };

  const renderEditor = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center items-end gap-2 pt-4 text-muted-foreground animate-pulse">
          <Spinner className="text-inherit" size="small" />
          <p>Loading</p>
        </div>
      );
    }
    if (loadingError) {
      return (
        <ErrorAlert
          className="mx-3"
          description={loadingError.message}
          title="There was a loading error"
        />
      );
    }
    if (query) {
      return (
        <QueryEditor
          key={query.id}
          query={query}
          setQuery={(query) => setQuery(query as Query)}
          updateText={updateText}
        />
      );
    }
    return null;
  };

  return (
    <QueryPage
      databaseId={databaseId}
      query={query}
      queryResult={queryResult}
      setQueryResult={setQueryResult}
    >
      {renderHeader()}
      {renderEditor()}
    </QueryPage>
  );
};

export default ProjectQueryPage;
