import { useState } from "react";
import { Button } from "react-bootstrap";

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
    <div className="row">
      <div className="col-3 border-end">
        <div className="d-flex justify-content-end mb-2">
          <Button
            size="sm"
            variant="primary"
            onClick={() => handleExecuteQuery()}
          >
            Execute
          </Button>
        </div>
        <QueryEditor query={query} />
      </div>
      <div className="col p-3 d-flex flex-column justify-content-end">
        <QueryResult success={success} result={queryResult} />
      </div>
    </div>
  );
};

export default QueryExplorer;
