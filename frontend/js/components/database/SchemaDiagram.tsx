import { ReactFlow, Background, Controls, Panel } from "@xyflow/react";
import type { Edge, Node } from "@xyflow/react";
import React, { useEffect, useMemo, useState } from "react";

import { Database, DatabasesService } from "api";
import "@xyflow/react/dist/style.css";
import { useErrorToast } from "js/hooks/useErrorToast";

import TableNode from "./TableNode";

interface SchemaDiagramProps {
  databaseId: number;
  children?: React.ReactNode;
}

const nodeTypes = {
  table: TableNode,
};

const SchemaDiagram = ({ databaseId, children }: SchemaDiagramProps) => {
  const toast = useErrorToast();
  const [database, setDatabase] = useState<Database>();
  const schema = database?.schema;

  useEffect(() => {
    const fetchDatabase = async () => {
      try {
        const result = await DatabasesService.databasesRetrieve({
          id: databaseId,
        });
        setDatabase(result);
      } catch (err) {
        setDatabase(undefined);
        toast({
          title: "Error loading database schema",
        });
      }
    };

    fetchDatabase();
  }, [databaseId]);

  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    if (!schema) {
      return { nodes, edges };
    }

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
      <Panel className="w-11/12 pb-2" position="bottom-center">
        {children}
      </Panel>
    </ReactFlow>
  );
};

export default SchemaDiagram;
