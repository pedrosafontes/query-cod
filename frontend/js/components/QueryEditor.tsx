import { useEffect, useRef, useState } from "react";
import MonacoEditor, { Monaco, loader } from "@monaco-editor/react";

import { QueriesService, Query, QueryError } from "../api";
import { useAutosave } from "../hooks/useAutosave";

const QueryEditor = ({ query }: { query: Query }) => {
  const [text, setText] = useState<string>(query.text);
  const [errors, setErrors] = useState<QueryError[]>([]);
  const monacoRef = useRef<Monaco | null>(null);
  const editorRef = useRef<any>(null);

  const updateQuery = async (queryText: string): Promise<void> => {
    try {
      const result = await QueriesService.queriesPartialUpdate({
        id: query.id,
        requestBody: {
          text: queryText,
        },
      });

      if (result.errors) {
        setErrors(result.errors);
      }
    } catch (err) {
      console.error("Error updating query:", err);
    }
  };

  const updateErrorMarkers = () => {
    if (!monacoRef.current || !editorRef.current) return;
    
    const model = editorRef.current.getModel();
    if (!model) return;
    
    if (errors.length > 0) {
      const markers = errors.map((error) => {
        return {
          startLineNumber: error.line,
          endLineNumber: error.line,
          startColumn: error.start_col,
          endColumn: error.end_col,
          message: error.message,
          severity: monacoRef.current!.MarkerSeverity.Error
        }
      })
      monacoRef.current.editor.setModelMarkers(model, "autosave-feedback", markers);
    } else {
      monacoRef.current.editor.setModelMarkers(model, "autosave-feedback", []);
    }
  };

  useEffect(() => {
    updateErrorMarkers();
  }, [errors]);

  const status = useAutosave({ data: text, onSave: updateQuery });

  const renderStatus = () => {
    switch (status) {
      case "saving":
        return <span className="text-muted">Saving...</span>;
      case "error":
        return <span className="text-danger">Error saving</span>;
      default:
        return <span className="text-success">Saved!</span>;
    }
  };

  return (
    <>
      <MonacoEditor
        height="400px"
        defaultLanguage="sql"
        value={text}
        onChange={(value) => setText(value || "")}
        theme="vs-dark"
        onMount={(editor, monaco) => {
          editorRef.current = editor;
          monacoRef.current = monaco;
          updateQuery(text)
        }}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: "on",
          tabSize: 2,
          lineNumbers: "on",
          formatOnType: true,
          formatOnPaste: true,
        }}
      />
      <div className="text-sm mt-2">{renderStatus()}</div>
    </>
  );
};

export default QueryEditor;
