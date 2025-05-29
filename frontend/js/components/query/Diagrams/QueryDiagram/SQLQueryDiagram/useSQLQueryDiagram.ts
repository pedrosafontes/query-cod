import { type Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { QueriesService, SQLTree } from "api";
import useLayout from "hooks/useLayout";

import getLayoutedNodes from "../layout";
import { QueryDiagramProps } from "../types";

import { SQLNode } from "./SQLNode";

const useSQLQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
  const [sqlTree, setSqlTree] = useState<SQLTree>();
  const [nodes, setNodes] = useState<SQLNode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!query) {
      setSqlTree(undefined);
      return;
    }

    const fetchRATree = async () => {
      const { sql_tree: sqlTree } = await QueriesService.queriesTreeRetrieve({
        id: query.id,
      });
      setSqlTree(sqlTree);
    };

    fetchRATree();
  }, [query]);

  useEffect(() => {
    const nodes: SQLNode[] = [];
    const edges: Edge[] = [];

    if (query && sqlTree) {
      const processTree = (tree: SQLTree) => {
        const { children, validation_errors: errors, ...data } = tree;
        const id = tree.id.toString();

        nodes.push({
          id,
          type: "sql",
          position: { x: 0, y: 0 },
          data: {
            queryId: query.id,
            setQueryResult,
            errors,
            ...data,
          },
          deletable: false,
        });
        if (children) {
          children.forEach((subTree) => {
            processTree(subTree);
            edges.push({
              id: `${id}-${subTree.id}`,
              type: "smoothstep",
              target: id,
              source: subTree.id.toString(),
              deletable: false,
              animated: true,
            });
          });
        }
      };

      processTree(sqlTree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [sqlTree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useSQLQueryDiagram;
