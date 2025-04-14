import { useEffect, useState } from "react";

import { Query } from "api";
import { QueryError } from "types/query";

import ErrorAlert from "./ErrorAlert";
import RelationalAlgebraEditor from "./RelationalAlgebraEditor";
import SQLEditor from "./SQLEditor";

type QueryEditorProps = {
  query: Query;
  onErrorsChange: (errors: QueryError[]) => void;
};

const QueryEditor = ({ query, onErrorsChange }: QueryEditorProps) => {
  const [errors, setErrors] = useState<QueryError[]>(query.validation_errors);

  const generalErrors = errors.filter(({ position }) => !position);

  useEffect(() => {
    onErrorsChange(query.validation_errors);
  }, [query.validation_errors, onErrorsChange]);

  const renderEditor = () => {
    switch (query.language) {
      case "sql":
        return <SQLEditor query={query} onErrorsChange={setErrors} />;
      case "ra":
        return (
          <RelationalAlgebraEditor query={query} onErrorsChange={setErrors} />
        );
      default:
        return null;
    }
  };

  return (
    <>
      {renderEditor()}
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
