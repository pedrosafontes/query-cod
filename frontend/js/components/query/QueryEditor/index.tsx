import { Query } from "api";

import RAEditor from "./RAEditor";
import SQLEditor from "./SQLEditor";

type QueryEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
};

const QueryEditor = ({ query, setQuery }: QueryEditorProps) => {
  const renderEditor = () => {
    switch (query.language) {
      case "sql":
        return <SQLEditor query={query} setQuery={setQuery} />;
      case "ra":
        return <RAEditor query={query} setQuery={setQuery} />;
      default:
        return null;
    }
  };

  return renderEditor();
};

export default QueryEditor;
