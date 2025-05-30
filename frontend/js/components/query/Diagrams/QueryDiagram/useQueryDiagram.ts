import { useContext } from "react";

import { QueryContext } from "contexts/QueryContext";

import useRAQueryDiagram from "./RAQueryDiagram/useRAQueryDiagram";
import useSQLQueryDiagram from "./SQLQueryDiagram/useSQLQueryDiagram";

const useQueryDiagram = () => {
  const { query, setQueryResult } = useContext(QueryContext)!;

  const raDiagram = useRAQueryDiagram({
    query,
    setQueryResult,
  });

  const sqlDiagram = useSQLQueryDiagram({
    query,
    setQueryResult,
  });

  switch (query?.language) {
    case "ra":
      return raDiagram;
    case "sql":
      return sqlDiagram;
    default:
      return { nodes: [], edges: [] };
  }
};

export default useQueryDiagram;
