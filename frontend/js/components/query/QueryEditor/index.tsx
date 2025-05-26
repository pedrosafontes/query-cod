import { QueriesService, Query } from "api";

import RAEditor from "./RAEditor";
import SQLEditor from "./SQLEditor";

type QueryEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
};

const QueryEditor = ({ query, setQuery }: QueryEditorProps) => {
  const updateText = async (value: string) => {
    const result = await QueriesService.queriesPartialUpdate({
      id: query.id,
      requestBody: { text: value },
    });
    setQuery(result);
  };

  const renderEditor = () => {
    switch (query.language) {
      case "sql":
        return <SQLEditor query={query} updateText={updateText} />;
      case "ra":
        return <RAEditor query={query} updateText={updateText} />;
      default:
        return null;
    }
  };

  return renderEditor();
};

export default QueryEditor;
