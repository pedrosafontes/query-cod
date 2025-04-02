import { useState } from "react";
import { Button, Table } from "react-bootstrap";

import { QueriesService, Query, QueryResultData } from "../api";

import QueryEditor from "./QueryEditor";

const QueryExplorer = ({ query }: { query: Query }) => {
  const [queryResult, setQueryResult] = useState<QueryResultData>();

  const handleExecuteQuery = async (): Promise<void> => {
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: query.id,
      });

      setQueryResult(execution.results);
    } catch (error) {
      console.error("Error executing query:", error);
    }
  };

  return (
    <div className="row">
      <div className="col-3">
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
      <div className="col">
        {queryResult && (
          <Table responsive>
            <thead>
              <tr>
                {queryResult.columns.map((column: string, index: number) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {queryResult.rows.map((row, index: number) => (
                <tr key={index}>
                  {row.map((cell: string | null, cellIndex: number) => (
                    <td key={`${index}-${cellIndex}`}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </div>
    </div>
  );
};

export default QueryExplorer;
