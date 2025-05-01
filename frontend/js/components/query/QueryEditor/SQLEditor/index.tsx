import MonacoEditor, { Monaco } from "@monaco-editor/react";
import partition from "lodash/partition";
import { editor } from "monaco-editor";
import { useEffect, useRef, useState } from "react";

import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";
import { QueryError } from "types/query";

import AutosaveStatus from "../AutosaveStatus";
import ErrorAlert from "../ErrorAlert";

type SQLEditorProps = {
  onErrorsChange: (errors: QueryError[]) => void;
  query: Query;
};

const SQLEditor = ({ query, onErrorsChange }: SQLEditorProps) => {
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const [value, setValue] = useState<string | undefined>(query.sql_text);
  const [errors, setErrors] = useState<QueryError[]>(query.validation_errors);
  const [editorErrors, generalErrors] = partition(errors, (e) => e.position);

  const updateErrorMarkers = () => {
    if (!monacoRef.current || !editorRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    if (errors.length > 0) {
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
    } else {
      monacoRef.current.editor.setModelMarkers(model, "autosave-feedback", []);
    }
  };

  useEffect(() => {
    onErrorsChange(errors);
  }, [errors]);

  useEffect(() => {
    updateErrorMarkers();
  }, [generalErrors]);

  const updateSqlText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { sql_text: value },
    });

    setErrors(result.validation_errors);
  };

  const status = useAutosave({ data: value, onSave: updateSqlText });

  return (
    <>
      <MonacoEditor
        defaultLanguage="sql"
        height="500px"
        loading={<Spinner className="text-gray-400" size="small" />}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: "on",
          tabSize: 2,
          lineNumbers: "on",
          formatOnType: true,
          formatOnPaste: true,
          lineNumbersMinChars: 2,
        }}
        theme="vs-light"
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
