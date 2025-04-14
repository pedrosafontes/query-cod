import { useEffect, useState } from "react";

import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import ErrorAlert from "./ErrorAlert";
import ExecuteQueryButton from "./ExecuteQueryButton";
import QueryEditor from "./QueryEditor";
import QueryLanguageTabs from "./QueryLanguageTabs";
import QueryResult from "./QueryResult";
import { Skeleton } from "./ui/skeleton";

export type QueryExplorerProps = {
  queryId: number;
};

const QueryExplorer = ({ queryId }: QueryExplorerProps) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isExecuting, setIsExecuting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingError, setLoadingError] = useState<Error | null>(null);
  const [hasErrors, setHasErrors] = useState(false);
  const toast = useErrorToast();

  const handleExecuteQuery = async (): Promise<void> => {
    setIsExecuting(true);
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: queryId,
      });

      setQueryResult(execution.results);
    } catch (err) {
      toast({
        title: "Error executing query",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  useEffect(() => {
    const fetchQuery = async () => {
      setIsLoading(true);
      setQueryResult(undefined);
      try {
        const result = await QueriesService.queriesRetrieve({
          id: queryId,
        });
        setQuery(result);
        setLoadingError(null);
      } catch (err) {
        setQuery(undefined);
        if (err instanceof Error) {
          setLoadingError(err);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuery();
  }, [queryId]);

  return (
    <div className="grid grid-cols-3 h-full">
      <div className="col-span-1 px-3 py-5 border-r">
        <div className="flex justify-between mb-5 w-full">
          {query && (
            <QueryLanguageTabs
              query={query}
              setIsLoading={setIsLoading}
              setQuery={setQuery}
            />
          )}
          {!query && <Skeleton className="h-10 w-52" />}
          <ExecuteQueryButton
            disabled={isExecuting || isLoading || !!loadingError || hasErrors}
            handleExecuteQuery={handleExecuteQuery}
            hasErrors={hasErrors}
            loading={isExecuting}
          />
        </div>
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <Spinner className="text-muted-foreground" />
          </div>
        )}
        {loadingError && (
          <ErrorAlert
            description={loadingError.message}
            title="There was an error loading the query"
          />
        )}
        {query && (
          <QueryEditor
            key={query.id}
            query={query}
            onErrorsChange={(errors) => setHasErrors(errors.length > 0)}
          />
        )}
      </div>
      <div className="col-span-2 px-3 py-5 flex flex-col justify-end h-full bg-gray-50">
        {queryResult && (
          <QueryResult isLoading={isExecuting} result={queryResult} />
        )}
      </div>
    </div>
  );
};

export default QueryExplorer;
