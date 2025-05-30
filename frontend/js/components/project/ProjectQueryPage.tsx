import { QueriesService, Query, QueryResultData } from "api";

import ExecuteQueryButton from "../query/ExecuteQueryButton";
import QueryEditor from "../query/QueryEditor";
import ErrorAlert from "../query/QueryEditor/ErrorAlert";
import QueryPage from "../query/QueryPage";
import TranspileQueryButton from "../query/TranspileQueryButton";
import { Spinner } from "../ui/spinner";

import { useProjectQuery } from "./useProjectQuery";

type ProjectQueryProps = {
  databaseId: number;
  queryId?: number;
  setQueryId: (queryId?: number) => void;
  refetchProject: () => void;
};

const ProjectQueryPage = ({
  databaseId,
  queryId,
  setQueryId,
  refetchProject,
}: ProjectQueryProps) => {
  const {
    query,
    setQuery,
    queryResult,
    setQueryResult,
    isLoading,
    loadingError,
    updateText,
  } = useProjectQuery(queryId);

  return (
    <QueryPage
      databaseId={databaseId}
      executeSubquery={QueriesService.queriesSubqueriesExecutionsCreate}
      fetchTree={QueriesService.queriesTreeRetrieve}
      query={query}
      queryResult={queryResult}
      setQueryResult={setQueryResult}
    >
      <ProjectQueryHeader
        query={query}
        refetchProject={refetchProject}
        setQueryId={setQueryId}
        setQueryResult={setQueryResult}
      />
      <ProjectQueryEditor
        isLoading={isLoading}
        loadingError={loadingError || undefined}
        query={query}
        setQuery={setQuery}
        updateText={updateText}
      />
    </QueryPage>
  );
};

type ProjectQueryEditorProps = {
  query?: Query;
  isLoading: boolean;
  loadingError?: Error;
  updateText: (text: string) => Promise<void>;
  setQuery: (query: Query) => void;
};

const ProjectQueryEditor = ({
  query,
  isLoading,
  loadingError,
  updateText,
  setQuery,
}: ProjectQueryEditorProps) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-end gap-2 pt-4 text-muted-foreground animate-pulse">
        <Spinner className="text-inherit" size="small" />
        <p>Loading</p>
      </div>
    );
  }
  if (loadingError) {
    return (
      <ErrorAlert
        className="mx-3 w-auto"
        description={loadingError.message}
        title="There was a loading error"
      />
    );
  }
  if (query) {
    return (
      <QueryEditor
        key={query.id}
        query={query}
        setQuery={(query) => setQuery(query as Query)}
        updateText={updateText}
      />
    );
  }
  return null;
};

type ProjectQueryHeaderProps = {
  query?: Query;
  setQueryId: (queryId?: number) => void;
  setQueryResult: (result?: QueryResultData) => void;
  refetchProject: () => void;
};

const ProjectQueryHeader = ({
  query,
  setQueryId,
  setQueryResult,
  refetchProject,
}: ProjectQueryHeaderProps) => {
  const hasErrors = !!query && query.validation_errors.length > 0;
  const disabled = !query || hasErrors;

  return (
    <div className="flex justify-between items-center gap-2 mb-5 w-full px-3">
      <h1 className="truncate">{query?.name}</h1>
      <div className="flex gap-2">
        <TranspileQueryButton
          disabled={disabled}
          query={query}
          setQueryId={setQueryId}
          showFixErrorsTooltip={hasErrors}
          onSuccess={refetchProject}
        />
        <ExecuteQueryButton
          disabled={disabled}
          query={query}
          setQueryResult={setQueryResult}
          showFixErrorsTooltip={hasErrors}
        />
      </div>
    </div>
  );
};

export default ProjectQueryPage;
