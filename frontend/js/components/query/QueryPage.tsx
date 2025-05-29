import { ReactFlowProvider } from "@xyflow/react";
import { ReactNode } from "react";

import { QueryResultData } from "api";

import Diagrams from "./Diagrams";
import QueryPanels from "./QueryPanels";
import QueryResult from "./QueryResult";
import { Query } from "./types";

export type QueryPageProps = {
  children: ReactNode;
  databaseId: number;
  query?: Query;
  queryResult?: QueryResultData;
  setQueryResult: (result?: QueryResultData) => void;
};

const QueryPage = ({
  children,
  databaseId,
  query,
  queryResult,
  setQueryResult,
}: QueryPageProps) => {
  return (
    <QueryPanels
      left={children}
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
