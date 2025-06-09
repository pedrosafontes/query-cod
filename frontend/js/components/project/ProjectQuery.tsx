import { useEffect, useState } from "react";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { QueriesService, Query, QueryResultData } from "api";

import ExecuteQueryButton from "../query/ExecuteQueryButton";
import QueryEditor from "../query/QueryEditor";
import ErrorAlert from "../query/QueryEditor/ErrorAlert";
import QueryPage from "../query/QueryPage";
import TranspileQueryButton from "../query/TranspileQueryButton";
import { Spinner } from "../ui/spinner";

import Assistant from "./Assistant";
import { useProjectQuery } from "./useProjectQuery";

export type ProjectQueryProps = {
  databaseId: number;
  queryId?: number;
  setQueryId: (queryId?: number) => void;
  refetchProject: () => void;
};

const ProjectQuery = ({
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

  const [tab, setTab] = useState<Tab>(Tab.Editor);

  useEffect(() => {
    setTab(Tab.Editor);
  }, [queryId]);

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
        setTab={setTab}
        tab={tab}
      />
      {tab === Tab.Editor && (
        <ProjectQueryEditor
          isLoading={isLoading}
          loadingError={loadingError || undefined}
          query={query}
          setQuery={setQuery}
          updateText={updateText}
        />
      )}
      {tab === Tab.Assistant && query && (
        <Assistant key={query.id} query={query} />
      )}
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
  tab: Tab;
  setQueryId: (queryId?: number) => void;
  setQueryResult: (result?: QueryResultData) => void;
  setTab: (tab: Tab) => void;
  refetchProject: () => void;
};

enum Tab {
  Editor = "editor",
  Assistant = "assistant",
}

const ProjectQueryHeader = ({
  query,
  tab,
  setQueryId,
  setQueryResult,
  setTab,
  refetchProject,
}: ProjectQueryHeaderProps) => {
  const hasErrors = !!query && query.validation_errors.length > 0;
  const disabled = !query || hasErrors;

  return (
    <div className="flex justify-between gap-2 mb-5 w-full px-3">
      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)}>
        <TabsList>
          <TabsTrigger value="editor">Editor</TabsTrigger>
          <TabsTrigger value="assistant">Assistant</TabsTrigger>
        </TabsList>
      </Tabs>
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

export default ProjectQuery;
