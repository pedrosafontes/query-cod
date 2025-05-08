import { Monaco } from "@monaco-editor/react";
import partition from "lodash/partition";
import { editor } from "monaco-editor";
import { useEffect, useRef, useState } from "react";

import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import AutosaveStatus from "../AutosaveStatus";
import CodeEditor from "../CodeEditor";
import ErrorAlert from "../ErrorAlert";

type SQLEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
};

const SQLEditor = ({ query, setQuery }: SQLEditorProps) => {
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const [value, setValue] = useState<string | undefined>(query.sql_text);
  const [editorErrors, generalErrors] = partition(
    query.validation_errors,
    (e) => e.position,
  );

  const updateErrorMarkers = () => {
    if (!monacoRef.current || !editorRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    const markers = editorErrors.map(({ description, position }) => {
      return {
        startLineNumber: position!.line,
        endLineNumber: position!.line,
        startColumn: position!.start_col,
        endColumn: position!.end_col,
        message: description as string,
        severity: monacoRef.current!.MarkerSeverity.Error,
      };
    });
    monacoRef.current.editor.setModelMarkers(
      model,
      "autosave-feedback",
      markers,
    );
  };

  useEffect(() => {
    updateErrorMarkers();
  }, [generalErrors]);

  const updateSqlText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { sql_text: value },
    });
    setQuery(result);
  };

  const status = useAutosave({ data: value, onSave: updateSqlText });

  return (
    <>
      <CodeEditor
        className="max-h-[400px]"
        language="sql"
        options={{
          lineNumbers: "off",
        }}
        value={value}
        onChange={setValue}
        onMount={(editor, monaco) => {
          editorRef.current = editor;
          monacoRef.current = monaco;
          updateErrorMarkers();
        }}
      />
      <div className="flex justify-end text-xs mt-2">
        <AutosaveStatus status={status} />
      </div>

      {generalErrors.length > 0 &&
        generalErrors.map((error) => (
          <ErrorAlert
            key={error.title + error.description}
            className="mt-4"
            description={error.description}
            hint={error.hint}
            title={error.title}
          />
        ))}
    </>
  );
};

export default SQLEditor;
