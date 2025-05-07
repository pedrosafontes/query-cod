import { Handle, Position } from "@xyflow/react";
import type { Node, NodeProps } from "@xyflow/react";
import { KeyRound } from "lucide-react";

import { Database } from "api";

type SchemaNodeData = {
  table: string;
  fields: Database["schema"][string];
};
export type SchemaNode = Node<SchemaNodeData, "table">;

const SchemaDiagramNode = ({ data }: NodeProps<SchemaNode>) => {
  const { table, fields } = data;

  return (
    <div className="bg-white border rounded-lg overflow-hidden text-sm">
      <h4 className="px-2 py-1 bg-black text-white">{table}</h4>
      <ul className="list-none font-light">
        {Object.entries(fields).map(
          ([col, { type: dataType, primary_key: primaryKey }]) => (
            <li
              key={col}
              className="relative flex justify-between items-center px-2 py-1 border-t"
            >
              <Handle
                className="invisible"
                id={`${table}.${col}`}
                position={Position.Left}
                type="target"
              />
              <div
                className={`flex items-center mr-5 ${primaryKey ? "font-semibold" : ""}`}
              >
                {primaryKey && <KeyRound className="w-3 h-3 mr-1" />}
                {col}
              </div>
              <span className="text-[9px] text-muted-foreground uppercase">
                {dataType}
              </span>
              <Handle
                className="invisible"
                id={`${table}.${col}`}
                position={Position.Right}
                type="source"
              />
            </li>
          ),
        )}
      </ul>
    </div>
  );
};

export default SchemaDiagramNode;
