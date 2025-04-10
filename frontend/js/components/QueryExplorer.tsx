import { Play } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import ErrorAlert from "./ErrorAlert";
import QueryEditor from "./QueryEditor";
import QueryResult from "./QueryResult";

export type QueryExplorerProps = {
  queryId: number;
};

const QueryExplorer = ({ queryId }: QueryExplorerProps) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isExecuting, setIsExecuting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
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
      try {
        const result = await QueriesService.queriesRetrieve({
          id: queryId,
        });
        setQuery(result);
        setError(null);
      } catch (err) {
        setQuery(undefined);
        if (err instanceof Error) {
          setError(err);
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
        <div className="flex justify-end mb-3 w-full">
          <Button
            disabled={isExecuting}
            size="sm"
            variant="default"
            onClick={() => handleExecuteQuery()}
          >
            {isExecuting ? (
              <Spinner className="text-primary-foreground" size="small" />
            ) : (
              <Play />
            )}
            Execute
          </Button>
        </div>
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <Spinner className="text-muted-foreground" />
          </div>
        )}
        {error && (
          <ErrorAlert
            description={error.message}
            title="There was an error loading the query"
          />
        )}
        {query && <QueryEditor key={query.id} query={query} />}
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
