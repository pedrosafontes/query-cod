import { useEffect, useState } from "react";

import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import SchemaDiagram from "../database/SchemaDiagram";
import { Skeleton } from "../ui/skeleton";

import ExecuteQueryButton from "./ExecuteQueryButton";
import QueryEditor from "./QueryEditor";
import ErrorAlert from "./QueryEditor/ErrorAlert";
import QueryLanguageTabs from "./QueryLanguageTabs";
import QueryResult from "./QueryResult";

export type QueryExplorerProps = {
  queryId: number;
  databaseId: number;
};

const QueryExplorer = ({ queryId, databaseId }: QueryExplorerProps) => {
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
    <div className="flex h-full">
      <div className="w-[400px] px-3 py-5 h-full border-r overflow-auto">
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
      <div className="flex-1 h-full w-full bg-gray-50">
        <SchemaDiagram databaseId={databaseId}>
          {queryResult && (
            <QueryResult isLoading={isExecuting} result={queryResult} />
          )}
        </SchemaDiagram>
      </div>
    </div>
  );
};

export default QueryExplorer;
