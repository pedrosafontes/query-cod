import useRAQueryDiagram from "./RAQueryDiagram/useRAQueryDiagram";
import useSQLQueryDiagram from "./SQLQueryDiagram/useSQLQueryDiagram";
import { QueryDiagramProps } from "./types";

const useQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
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
