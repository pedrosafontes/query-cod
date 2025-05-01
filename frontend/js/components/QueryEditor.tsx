import { Query } from "api";
import { QueryError } from "types/query";

import RelationalAlgebraEditor from "./RelationalAlgebraEditor";
import SQLEditor from "./SQLEditor";

type QueryEditorProps = {
  query: Query;
  onErrorsChange: (errors: QueryError[]) => void;
};

const QueryEditor = ({ query, onErrorsChange }: QueryEditorProps) => {
  const renderEditor = () => {
    switch (query.language) {
      case "sql":
        return <SQLEditor query={query} onErrorsChange={onErrorsChange} />;
      case "ra":
        return (
          <RelationalAlgebraEditor
            query={query}
            onErrorsChange={onErrorsChange}
          />
        );
      default:
        return null;
    }
  };

  return renderEditor();
};

export default QueryEditor;
