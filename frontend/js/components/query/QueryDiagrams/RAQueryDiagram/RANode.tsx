import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import LatexFormula from "../../QueryEditor/RelationalAlgebraEditor/LatexFormula";

type RANodeData = {
  label: string;
};
export type RANode = Node<RANodeData, "ra">;

const RADiagramNode = ({ data }: NodeProps<RANode>) => {
  const { label } = data;

  return (
    <div className="bg-white border rounded-lg p-2">
      <Handle
        className="invisible size-0 border-0 top-1"
        position={Position.Top}
        type="target"
      />
      <LatexFormula expression={label} />
      <Handle
        className="invisible size-0 border-0 bottom-1"
        position={Position.Bottom}
        type="source"
      />
    </div>
  );
};

export default RADiagramNode;
