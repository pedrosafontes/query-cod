import { Play } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import QueryEditor from "./QueryEditor";
import QueryResult from "./QueryResult";

export type QueryExplorerProps = {
  queryId: number;
};

const QueryExplorer = ({ queryId }: QueryExplorerProps) => {
  const [query, setQuery] = useState<Query>();
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [isLoading, setIsLoading] = useState(false);
  const toast = useErrorToast();

  const handleExecuteQuery = async (): Promise<void> => {
    setIsLoading(true);
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: queryId,
      });

      setQueryResult(execution.results);
    } catch (error) {
      toast({
        title: "Error executing query",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const fetchQuery = async () => {
      try {
        const result = await QueriesService.queriesRetrieve({
          id: queryId,
        });
        setQuery(result);
      } catch (error) {
        setQuery(undefined);
        toast({
          title: "Error loading query",
        });
      }
    };

    fetchQuery();
  }, [queryId]);

  return (
    <div className="grid grid-cols-3 h-full">
      <div className="col-span-1 px-3 py-5 border-r">
        <div className="flex justify-end mb-3 w-full">
          <Button
            disabled={isLoading}
            size="sm"
            variant="default"
            onClick={() => handleExecuteQuery()}
          >
            {isLoading ? (
              <Spinner className="text-primary-foreground" size="small" />
            ) : (
              <Play />
            )}
            Execute
          </Button>
        </div>
        {query && <QueryEditor key={query.id} query={query} />}
      </div>
      <div className="col-span-2 px-3 py-5 flex flex-col justify-end h-full bg-gray-50">
        {queryResult && (
          <QueryResult isLoading={isLoading} result={queryResult} />
        )}
      </div>
    </div>
  );
};

export default QueryExplorer;
