import { Query } from "components/query/types";

import RAEditor from "./RAEditor";
import SQLEditor from "./SQLEditor";

type QueryEditorProps = {
  query: Query;
  setQuery: (query: Query) => void;
  updateText: (text: string) => Promise<void>;
};

const QueryEditor = ({ query, updateText }: QueryEditorProps) => {
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
