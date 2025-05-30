import {
  Attempt,
  AttemptsSubqueriesExecutionsCreateResponse,
  AttemptsTreeRetrieveResponse,
  Query as ProjectQuery,
  QueriesSubqueriesExecutionsCreateResponse,
  QueriesTreeRetrieveResponse,
} from "api";

export type Query = ProjectQuery | Attempt;

type SubqueriesResponse =
  | QueriesTreeRetrieveResponse
  | AttemptsTreeRetrieveResponse;
export type FetchTree = (data: { id: number }) => Promise<SubqueriesResponse>;

type SubqueryExecutionResponse =
  | QueriesSubqueriesExecutionsCreateResponse
  | AttemptsSubqueriesExecutionsCreateResponse;
export type ExecuteSubquery = (data: {
  id: number;
  subqueryId: number;
}) => Promise<SubqueryExecutionResponse>;
