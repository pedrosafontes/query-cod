import { useState } from "react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-tomorrow";
import { useAutosave } from "react-autosave";

import { QueriesService, Query } from "../api";

const QueryEditor = ({ query }: { query: Query }) => {
  const [text, setText] = useState<string>(query.text);

  const updateQuery = async (queryText: string): Promise<void> => {
    try {
      await QueriesService.queriesPartialUpdate({
        id: query.id,
        requestBody: {
          text: queryText,
        },
      });
    } catch (error) {
      console.error("Error updating query:", error);
    }
  };

  useAutosave({ data: text, onSave: updateQuery, interval: 1000 });

  return (
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
  );
};

export default QueryEditor;
