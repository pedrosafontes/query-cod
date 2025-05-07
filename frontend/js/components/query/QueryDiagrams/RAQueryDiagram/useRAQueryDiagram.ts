import type { Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { RATree } from "api";

import getTreeNodes from "./layout";
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

    const processTree = (node: RATree) => {
      nodes.push({
        id: node.id.toString(),
        type: "ra",
        position: { x: 0, y: 0 },
        data: {
          label: node.label,
        },
      });
      if (node.sub_trees) {
        node.sub_trees.forEach((sub_tree) => {
          processTree(sub_tree);
          edges.push({
            id: `${node.id}-${sub_tree.id}`,
            type: "smoothstep",
            source: node.id.toString(),
            target: sub_tree.id.toString(),
          });
        });
      }
    };

    if (tree) {
      processTree(tree);
    }

    const layoutedNodes = getTreeNodes({
      nodes,
      edges,
    });

    setNodes(layoutedNodes as RANode[]);
    setEdges(edges);
  }, [tree, setNodes, setEdges]);

  return { nodes, edges };
};

export default useRAQueryDiagram;
