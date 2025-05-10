import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { QueriesService, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import LatexFormula from "../../QueryEditor/RAEditor/LatexFormula";

type RANodeData = {
  queryId: number;
  id: number;
  label: string;
  setQueryResult: (result?: QueryResultData) => void;
};
export type RANode = Node<RANodeData, "ra">;

const RADiagramNode = ({ data }: NodeProps<RANode>) => {
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const toast = useErrorToast();
  const { queryId, id, label, setQueryResult } = data;

  const handleExecuteSubquery = async (): Promise<void> => {
    setIsExecuting(true);
    try {
      const execution = await QueriesService.queriesSubqueriesExecutionsCreate({
        id: queryId,
        subqueryId: id,
      });

      setQueryResult(execution.results);
    } catch (err) {
      toast({
        title: "Error executing subquery",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <Button
      className={`bg-white border transition-colors\
        ${isExecuting && "cursor-wait animate-[pulse-scale_1s_ease-in-out_infinite] bg-gray-100"}
        `}
      variant="ghost"
      onClick={handleExecuteSubquery}
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
