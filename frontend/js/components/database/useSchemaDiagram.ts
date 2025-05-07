import type { Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { Database, DatabasesService } from "api";
import "@xyflow/react/dist/style.css";
import { useErrorToast } from "hooks/useErrorToast";

import getLayoutedNodes from "./layout";
import { SchemaNode } from "./SchemaNode";

export type SchemaDiagramProps = {
  databaseId: number;
};

const useSchemaDiagram = ({ databaseId }: SchemaDiagramProps) => {
  const toast = useErrorToast();
  const [database, setDatabase] = useState<Database>();
  const schema = database?.schema;
  const [nodes, setNodes] = useState<SchemaNode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

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

  useEffect(() => {
    const createDiagram = async () => {
      const nodes: SchemaNode[] = [];
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
              type: "smoothstep",
            });
          }
        });
      });

      const layoutedNodes = await getLayoutedNodes({ nodes, edges });

      setNodes(layoutedNodes);
      setEdges(edges);
    };

    createDiagram();
  }, [schema, setNodes, setEdges]);

  return { nodes, edges };
};

export default useSchemaDiagram;
