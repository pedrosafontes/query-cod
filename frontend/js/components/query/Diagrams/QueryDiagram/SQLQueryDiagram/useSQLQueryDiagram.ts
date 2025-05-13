import { type Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { SQLTree } from "api";
import useLayout from "hooks/useLayout";

import getLayoutedNodes from "../layout";
import { QueryDiagramProps } from "../types";

import { SQLNode } from "./SQLNode";

const useRAQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
  const [nodes, setNodes] = useState<SQLNode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    const nodes: SQLNode[] = [];
    const edges: Edge[] = [];

    if (query?.sql_tree) {
      const processTree = (tree: SQLTree) => {
        const { children, ...data } = tree;
        const id = tree.id.toString();

        nodes.push({
          id,
          type: "sql",
          position: { x: 0, y: 0 },
          data: {
            ...data,
            queryId: query.id,
            setQueryResult,
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

      processTree(query.sql_tree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [query?.ra_tree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useRAQueryDiagram;
