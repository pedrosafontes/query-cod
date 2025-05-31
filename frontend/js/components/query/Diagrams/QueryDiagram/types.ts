import { QueryResultData } from "api";
import { Query } from "components/query/types";

export type QueryDiagramProps = {
  query?: Query;
  setQueryResult: (result?: QueryResultData) => void;
};
