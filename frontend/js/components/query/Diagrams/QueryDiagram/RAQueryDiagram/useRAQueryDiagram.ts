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
    if (!query) {
      setRaTree(undefined);
      return;
    }

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
      const processTree = (tree: RATree) => {
        const { children, validation_errors: errors, ...data } = tree;
        const id = tree.id.toString();

        nodes.push({
          id,
          type: "ra",
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

      processTree(raTree);
    }

    setNodes(nodes);
    setEdges(edges);
  }, [raTree]);

  useLayout({ layout: getLayoutedNodes });

  return { nodes, edges };
};

export default useRAQueryDiagram;
