import { useState } from "react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-tomorrow";

import { QueriesService, Query } from "../api";
import { useAutosave } from "../hooks/useAutosave";

const QueryEditor = ({ query }: { query: Query }) => {
  const [text, setText] = useState<string>(query.text);
  const [error, setError] = useState<string | undefined>(undefined);

  const updateQuery = async (queryText: string): Promise<void> => {
    try {
      const result = await QueriesService.queriesPartialUpdate({
        id: query.id,
        requestBody: {
          text: queryText,
        },
      });
      setError(result.error);
    } catch (error) {
      console.error("Error updating query:", error);
    }
  };

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
  }

  return (
    <>
      <AceEditor
        highlightActiveLine
        mode="mysql"
        name="query_explorer"
        placeholder="Enter your SQL query here..."
        setOptions={{
          showLineNumbers: true,
          tabSize: 2,
        }}
        showGutter
        showPrintMargin
        theme="tomorrow"
        value={text}
        width="100%"
        onChange={(newText: string) => setText(newText)}
      />
      <div className="text-sm">
        {renderStatus()}
      </div>
      {error && (
        <div className="text-danger mt-2">
          {error}
        </div>
      )}
    </>
  );
};

export default QueryEditor;
