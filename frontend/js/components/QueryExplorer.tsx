import { Play } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

import { QueriesService, Query, QueryResultData } from "../api";

import QueryEditor from "./QueryEditor";
import QueryResult from "./QueryResult";

const QueryExplorer = ({ query }: { query: Query }) => {
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [success, setSuccess] = useState<boolean>(true);

  const handleExecuteQuery = async (): Promise<void> => {
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: query.id,
      });

      setQueryResult(execution.results);
      setSuccess(execution.success);
    } catch (error) {
      console.error("Error executing query:", error);
    }
  };

  return (
    <div className="grid grid-cols-3 h-full">
      <div className="col-span-1 px-3 py-5 border-r">
        <div className="flex justify-end mb-3 w-full">
          <Button
            size="sm"
            variant="default"
            onClick={() => handleExecuteQuery()}
          >
            <Play />
            Execute
          </Button>
        </div>
        <QueryEditor key={query.id} query={query} />
      </div>
      <div className="col-span-2 px-3 py-5 flex flex-col justify-end h-full bg-gray-50">
        <QueryResult result={queryResult} success={success} />
      </div>
    </div>
  );
};

export default QueryExplorer;
