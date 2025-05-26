import { Monaco } from "@monaco-editor/react";
import partition from "lodash/partition";
import { editor } from "monaco-editor";
import { useEffect, useRef, useState } from "react";

import { Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import AutosaveStatus from "../AutosaveStatus";
import CodeEditor from "../CodeEditor";
import ErrorAlert from "../ErrorAlert";

type SQLEditorProps = {
  query: Query;
  updateText: (text: string) => Promise<void>;
};

const SQLEditor = ({ query, updateText }: SQLEditorProps) => {
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const [value, setValue] = useState<string | undefined>(query.text);
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

  const status = useAutosave({ data: value, onSave: updateText });

  return (
    <>
      <CodeEditor
        className="max-h-[400px] -mx-3 border-b"
        language="sql"
        options={{
          lineNumbers: "on",
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
