import { Handle, Position } from "@xyflow/react";
import type { Node, NodeProps } from "@xyflow/react";

import { Database } from "js/api";

type TableNodeData = {
  table: string;
  fields: Database["schema"][string];
};
type TableNodeProps = Node<TableNodeData, "table">;

const TableNode = ({ data }: NodeProps<TableNodeProps>) => {
  const { table, fields } = data;

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      <h4 className="px-2 py-1 text-sm bg-black text-white">{table}</h4>
      <ul className="list-none">
        {Object.entries(fields).map(([col, { type: dataType }]) => (
          <li
            key={col}
            className="relative flex justify-between items-center px-2 py-1 border-t"
          >
            <Handle
              className="invisible"
              id={col}
              position={Position.Left}
              type="target"
            />
            <span className="text-sm mr-5">{col}</span>
            <span className="text-[9px] text-muted-foreground uppercase">
              {dataType}
            </span>
            <Handle
              className="invisible"
              id={col}
              position={Position.Right}
              type="source"
            />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TableNode;
