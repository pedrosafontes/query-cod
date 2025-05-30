import { ReactFlowProvider } from "@xyflow/react";
import { ReactNode } from "react";

import { QueryResultData } from "api";
import { QueryContext } from "contexts/QueryContext";

import Diagrams from "./Diagrams";
import QueryPanels from "./QueryPanels";
import QueryResult from "./QueryResult";
import { ExecuteSubquery, FetchTree, Query } from "./types";

export type QueryPageProps = {
  children: ReactNode;
  databaseId: number;
  query?: Query;
  queryResult?: QueryResultData;
  setQueryResult: (result?: QueryResultData) => void;
  fetchTree: FetchTree;
  executeSubquery: ExecuteSubquery;
  minLeftWidth?: number;
};

const QueryPage = ({
  children,
  databaseId,
  query,
  queryResult,
  setQueryResult,
  fetchTree,
  executeSubquery,
  minLeftWidth,
}: QueryPageProps) => {
  return (
    <QueryPanels
      left={children}
      minLeftWidth={minLeftWidth}
      right={
        <ReactFlowProvider>
          <QueryContext.Provider
            value={{ query, setQueryResult, fetchTree, executeSubquery }}
          >
            <Diagrams databaseId={databaseId}>
              {queryResult && <QueryResult result={queryResult} />}
            </Diagrams>
          </QueryContext.Provider>
        </ReactFlowProvider>
      }
    />
  );
};

export default QueryPage;
