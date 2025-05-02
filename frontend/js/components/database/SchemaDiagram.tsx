import { ReactFlow, Background, Controls, Panel } from "@xyflow/react";
import type { Edge, Node } from "@xyflow/react";
import React, { useMemo } from "react";

import { Database } from "js/api";
import "@xyflow/react/dist/style.css";

import TableNode from "./TableNode";

interface SchemaDiagramProps {
  schema: Database["schema"];
  children?: React.ReactNode;
}

const nodeTypes = {
  table: TableNode,
};

const SchemaDiagram = ({ schema, children }: SchemaDiagramProps) => {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    const xSpacing = 300;
    const ySpacing = 200;

    Object.entries(schema).forEach(([table, fields], i) => {
      nodes.push({
        id: table,
        type: "table",
        position: { x: (i % 3) * xSpacing, y: Math.floor(i / 3) * ySpacing },
        data: {
          table,
          fields,
        },
      });
    });

    Object.entries(schema).forEach(([table, fields]) => {
      Object.entries(fields).forEach(([col, field]) => {
        if (field.references) {
          const ref = field.references;
          edges.push({
            id: `${table}.${col}-${ref.table}.${ref.column}`,
            source: table,
            sourceHandle: col,
            target: ref.table,
            targetHandle: ref.column,
          });
        }
      });
    });

    return { nodes, edges };
  }, [schema]);

  return (
    <ReactFlow edges={edges} fitView nodeTypes={nodeTypes} nodes={nodes}>
      <Background />
      <Controls />
      <Panel className="w-11/12" position="bottom-center">
        {children}
      </Panel>
    </ReactFlow>
  );
};

export default SchemaDiagram;
