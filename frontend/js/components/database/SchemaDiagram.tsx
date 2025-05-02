import {
  ReactFlow,
  Background,
  Controls,
  Panel,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import type { Edge } from "@xyflow/react";
import React, { useEffect, useState } from "react";

import { Database, DatabasesService } from "api";
import "@xyflow/react/dist/style.css";
import { useErrorToast } from "hooks/useErrorToast";
import useLayoutNodes from "hooks/useLayoutNodes";

import SchemaTable, { TableNode } from "./SchemaTable";

interface SchemaDiagramProps {
  databaseId: number;
  children?: React.ReactNode;
}

const nodeTypes = {
  table: SchemaTable,
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

  const [nodes, setNodes, onNodesChange] = useNodesState<TableNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    const nodes: TableNode[] = [];
    const edges: Edge[] = [];

    if (!schema) {
      return;
    }

    Object.entries(schema).forEach(([table, fields]) => {
      nodes.push({
        id: table,
        type: "table",
        position: { x: 0, y: 0 },
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
            sourceHandle: `${table}.${col}`,
            target: ref.table,
            targetHandle: `${ref.table}.${ref.column}`,
          });
        }
      });
    });

    setNodes(nodes);
    setEdges(edges);
  }, [schema, setNodes, setEdges]);

  useLayoutNodes();

  return (
    <ReactFlow
      edges={edges}
      fitView
      nodeTypes={nodeTypes}
      nodes={nodes}
      onEdgesChange={onEdgesChange}
      onNodesChange={onNodesChange}
    >
      <Background />
      <Controls />
      <Panel className="w-11/12 pb-2" position="bottom-center">
        {children}
      </Panel>
    </ReactFlow>
  );
};

export default SchemaDiagram;
