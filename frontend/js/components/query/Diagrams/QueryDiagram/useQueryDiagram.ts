import useRAQueryDiagram from "./RAQueryDiagram/useRAQueryDiagram";
import { QueryDiagramProps } from "./types";

const useQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
  const { nodes: RANodes, edges: RAEdges } = useRAQueryDiagram({
    query,
    setQueryResult,
  });

  switch (query?.language) {
    case "ra":
      return { nodes: RANodes, edges: RAEdges };
    case "sql":
      return { nodes: [], edges: [] };
    default:
      return { nodes: [], edges: [] };
  }
};

export default useQueryDiagram;
