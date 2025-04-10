import MonacoEditor, { Monaco } from "@monaco-editor/react";
import { partition } from "lodash";
import { AlertTriangle, CheckCircle } from "lucide-react";
import { editor } from "monaco-editor";
import { useEffect, useRef, useState } from "react";

import { Spinner } from "@/components/ui/spinner";
import { QueriesService, Query, QueryError } from "api";
import { useAutosave } from "hooks/useAutosave";

import ErrorAlert from "./ErrorAlert";

type QueryEditorProps = {
  query: Query;
  onErrorsChange: (errors: QueryError[]) => void;
};

const QueryEditor = ({ query, onErrorsChange }: QueryEditorProps) => {
  const [text, setText] = useState<string>(query.text);
  const [errors, setErrors] = useState<QueryError[]>(query.errors);
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const [editorErrors, generalErrors] = partition(errors, (e) => e.position);

  const updateQuery = async (queryText: string): Promise<void> => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: {
        text: queryText,
      },
    });

    setErrors(result.errors);
    onErrorsChange(result.errors);
  };

  const updateErrorMarkers = () => {
    if (!monacoRef.current || !editorRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    if (editorErrors.length > 0) {
      const markers = editorErrors.map(({ message, position }) => {
        return {
          startLineNumber: position!.line,
          endLineNumber: position!.line,
          startColumn: position!.start_col,
          endColumn: position!.end_col,
          message,
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
    updateErrorMarkers();
  }, [editorErrors]);

  useEffect(() => {
    onErrorsChange(query.errors);
  }, [query.errors, onErrorsChange]);

  const status = useAutosave({ data: text, onSave: updateQuery });

  const renderStatus = () => {
    switch (status) {
      case "saving":
        return (
          <span className="inline-flex items-center gap-1 text-gray-400 animate-pulse">
            <Spinner size="xs" />
            Saving...
          </span>
        );
      case "error":
        return (
          <span className="inline-flex items-center gap-1 text-destructive">
            <AlertTriangle className="h-3 w-3" />
            Error saving
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-green-600">
            <CheckCircle className="h-3 w-3" />
            Saved
          </span>
        );
    }
  };

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
        value={text}
        onChange={(value) => setText(value || "")}
        onMount={(editor, monaco) => {
          editorRef.current = editor;
          monacoRef.current = monaco;
          updateErrorMarkers();
        }}
      />
      <div className="flex justify-end text-xs mt-2">{renderStatus()}</div>
      {generalErrors.length > 0 && (
        <ErrorAlert
          className="mt-4"
          description={
            <ul className="list-disc list-inside space-y-1">
              {generalErrors.map((error, i) => (
                <li key={i}>{error.message}</li>
              ))}
            </ul>
          }
          title="Query validation failed"
        />
      )}
    </>
  );
};

export default QueryEditor;
