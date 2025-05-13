import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { Button } from "@/components/ui/button";
import { QueryResultData } from "api";
import LatexFormula from "components/query/QueryEditor/RAEditor/LatexFormula";

import useExecuteSubquery from "../useExecuteSubquery";

export type RANodeData = {
  queryId: number;
  id: number;
  label: string;
  setQueryResult: (result?: QueryResultData) => void;
};
export type RANode = Node<RANodeData, "ra">;

const RADiagramNode = ({ data }: NodeProps<RANode>) => {
  const { queryId, id, label, setQueryResult } = data;
  const { isExecuting, executeSubquery } = useExecuteSubquery({
    queryId,
    subqueryId: id,
    setQueryResult,
  });

  return (
    <Button
      className={`bg-white border transition-colors\
        ${isExecuting && "cursor-wait animate-[pulse-scale_1s_ease-in-out_infinite] bg-gray-100"}
        `}
      variant="ghost"
      onClick={executeSubquery}
    >
      <Handle
        className="invisible size-0 border-0 top-1"
        position={Position.Top}
        type="source"
      />
      <LatexFormula expression={label} />
      <Handle
        className="invisible size-0 border-0 bottom-1"
        position={Position.Bottom}
        type="target"
      />
    </Button>
  );
};

export default RADiagramNode;
