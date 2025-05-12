import { type Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { RATree } from "api";
import useLayout from "hooks/useLayout";

import { QueryDiagramProps } from "../types";

import getLayoutedNodes from "./layout";
import { RANode } from "./RANode";

const useRAQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
  const [nodes, setNodes] = useState<RANode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    const nodes: RANode[] = [];
    const edges: Edge[] = [];

    if (query?.ra_tree) {
      const processTree = ({ id, label, sub_trees: subTrees }: RATree) => {
        nodes.push({
          id: id.toString(),
          type: "ra",
          position: { x: 0, y: 0 },
          data: {
            queryId: query.id,
            id,
            label,
            setQueryResult,
          },
          deletable: false,
        });
        if (subTrees) {
          subTrees.forEach((subTree) => {
            processTree(subTree);
            edges.push({
              id: `${id}-${subTree.id}`,
              type: "smoothstep",
              target: id.toString(),
              source: subTree.id.toString(),
              deletable: false,
              animated: true,
            });
          });
        }
      };

      processTree(query.ra_tree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [query?.ra_tree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useRAQueryDiagram;
