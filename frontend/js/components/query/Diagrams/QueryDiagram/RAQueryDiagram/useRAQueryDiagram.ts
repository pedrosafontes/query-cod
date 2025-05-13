import { type Edge } from "@xyflow/react";
import { useEffect, useState } from "react";

import { QueriesService, RATree } from "api";
import useLayout from "hooks/useLayout";

import getLayoutedNodes from "../layout";
import { QueryDiagramProps } from "../types";

import { RANode } from "./RANode";

const useRAQueryDiagram = ({ query, setQueryResult }: QueryDiagramProps) => {
  const [raTree, setRaTree] = useState<RATree | undefined>();
  const [nodes, setNodes] = useState<RANode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!query) return;

    const fetchRATree = async () => {
      const { ra_tree: raTree } = await QueriesService.queriesTreeRetrieve({
        id: query.id,
      });
      setRaTree(raTree);
    };

    fetchRATree();
  }, [query]);

  useEffect(() => {
    const nodes: RANode[] = [];
    const edges: Edge[] = [];

    if (query && raTree) {
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

      processTree(raTree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [raTree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useRAQueryDiagram;
