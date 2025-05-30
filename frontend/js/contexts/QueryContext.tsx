import { createContext } from "react";

import { QueryResultData } from "api";
import { ExecuteSubquery, FetchTree, Query } from "components/query/types";

interface QueryContextType {
  query?: Query;
  setQueryResult: (result?: QueryResultData) => void;
  fetchTree: FetchTree;
  executeSubquery: ExecuteSubquery;
}

export const QueryContext = createContext<QueryContextType | null>(null);
