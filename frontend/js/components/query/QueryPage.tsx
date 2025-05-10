import { ReactFlowProvider } from "@xyflow/react";
import { useEffect, useState } from "react";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import { Skeleton } from "../ui/skeleton";

import ExecuteQueryButton from "./ExecuteQueryButton";
import QueryDiagrams from "./QueryDiagrams";
import QueryEditor from "./QueryEditor";
import ErrorAlert from "./QueryEditor/ErrorAlert";
import QueryLanguageTabs from "./QueryLanguageTabs";
import QueryResult from "./QueryResult";

export type QueryPageProps = {
  queryId: number;
  databaseId: number;
};

const QueryPage = ({ queryId, databaseId }: QueryPageProps) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isExecuting, setIsExecuting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingError, setLoadingError] = useState<Error | null>(null);
  const toast = useErrorToast();
  const hasErrors = !!query && query.validation_errors.length > 0;

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

  return (
    <ResizablePanelGroup direction="horizontal">
      <ResizablePanel className="min-w-[400px] px-3 py-5" defaultSize={0}>
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
          <QueryEditor key={query.id} query={query} setQuery={setQuery} />
        )}
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel className="bg-gray-50">
        <ReactFlowProvider>
          <QueryDiagrams
            databaseId={databaseId}
            query={query}
            setQueryResult={setQueryResult}
          >
            {queryResult && <QueryResult result={queryResult} />}
          </QueryDiagrams>
        </ReactFlowProvider>
      </ResizablePanel>
    </ResizablePanelGroup>
  );
};

export default QueryPage;
