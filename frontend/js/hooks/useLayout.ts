import {
  useReactFlow,
  useNodesInitialized,
  type Node,
  type Edge,
} from "@xyflow/react";
import { useEffect, useState } from "react";

type useLayoutProps = {
  layout: (data: { nodes: Node[]; edges: Edge[] }) => Promise<Node[]>;
};

export default function useLayout({ layout }: useLayoutProps) {
  const { getNodes, getEdges, setNodes } = useReactFlow();
  const nodesInitialized = useNodesInitialized();
  const [layoutedNodes, setLayoutedNodes] = useState(getNodes());

  useEffect(() => {
    const layoutNodes = async () => {
      if (nodesInitialized) {
        const nodes = getNodes();
        const edges = getEdges();
        const layouted = await layout({ nodes, edges });
        setLayoutedNodes(layouted);
      }
    };
    layoutNodes();
  }, [nodesInitialized, layout, getNodes, getEdges]);

  useEffect(() => {
    setNodes(layoutedNodes);
  }, [layoutedNodes, setNodes]);
}
