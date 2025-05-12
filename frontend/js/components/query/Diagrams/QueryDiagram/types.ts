import { Query, QueryResultData } from "api";

export type QueryDiagramProps = {
  query?: Query;
  setQueryResult: (result?: QueryResultData) => void;
};
