import { type Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { RATree } from "api";
import useLayout from "hooks/useLayout";

import getLayoutedNodes from "./layout";
import { RANode } from "./RANode";

export type RAQueryDiagramProps = {
  tree?: RATree;
};

const useRAQueryDiagram = ({ tree }: RAQueryDiagramProps) => {
  const [nodes, setNodes] = useState<RANode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    const nodes: RANode[] = [];
    const edges: Edge[] = [];

    const processTree = ({ id, label, sub_trees: subTrees }: RATree) => {
      nodes.push({
        id: id.toString(),
        type: "ra",
        position: { x: 0, y: 0 },
        data: {
          label,
        },
      });
      if (subTrees) {
        subTrees.forEach((subTree) => {
          processTree(subTree);
          edges.push({
            id: `${id}-${subTree.id}`,
            type: "smoothstep",
            source: id.toString(),
            target: subTree.id.toString(),
          });
        });
      }
    };

    if (tree) {
      processTree(tree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [tree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useRAQueryDiagram;
