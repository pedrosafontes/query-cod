import { ReactFlowProvider } from "@xyflow/react";
import { useEffect, useState } from "react";

import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";

import Diagrams from "./Diagrams";
import ExecuteQueryButton from "./ExecuteQueryButton";
import QueryEditor from "./QueryEditor";
import ErrorAlert from "./QueryEditor/ErrorAlert";
import QueryPanels from "./QueryPanels";
import QueryResult from "./QueryResult";
import TranspileQueryButton from "./TranspileQueryButton";

export type QueryPageProps = {
  queryId?: number;
  setQueryId: (queryId: number) => void;
  databaseId: number;
  onTranspile?: () => void;
};

const QueryPage = ({
  queryId,
  setQueryId,
  databaseId,
  onTranspile,
}: QueryPageProps) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isLoading, setIsLoading] = useState(false);
  const [loadingError, setLoadingError] = useState<Error | null>(null);
  const hasErrors = !!query && query.validation_errors.length > 0;
  const actionsDisabled = isLoading || !!loadingError;

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

  const renderEditor = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center items-end gap-2 pt-4 text-muted-foreground animate-pulse">
          <Spinner className="text-inherit" size="small" />
          <p>Loading query</p>
        </div>
      );
    }
    if (loadingError) {
      return (
        <ErrorAlert
          description={loadingError.message}
          title="There was an error loading the query"
        />
      );
    }
    if (query) {
      return <QueryEditor key={query.id} query={query} setQuery={setQuery} />;
    }
    return null;
  };

  return (
    <QueryPanels
      left={
        queryId && (
          <>
            <div className="flex justify-between items-center gap-2 mb-5 w-full px-3">
              <h1 className="truncate">{query && query.name}</h1>
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
            {renderEditor()}
          </>
        )
      }
      right={
        <ReactFlowProvider>
          <Diagrams
            databaseId={databaseId}
            query={query}
            setQueryResult={setQueryResult}
          >
            {queryResult && <QueryResult result={queryResult} />}
          </Diagrams>
        </ReactFlowProvider>
      }
    />
  );
};

export default QueryPage;
