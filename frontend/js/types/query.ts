import { Query } from "api";

export type QueryError = Query["validation_errors"][number];
