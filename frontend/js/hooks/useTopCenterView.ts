import {
  useReactFlow,
  getViewportForBounds,
  type Node,
  useStore,
} from "@xyflow/react";
import { useEffect } from "react";

export function useTopCenterFitView(nodes: Node[]) {
  const { setViewport, getNodesBounds } = useReactFlow();
  const width = useStore((state) => state.width);
  const height = useStore((state) => state.height);

  useEffect(() => {
    if (nodes.length === 0) return;

    const bounds = getNodesBounds(nodes);

    const { x, zoom } = getViewportForBounds(
      bounds,
      width,
      height,
      0.5,
      2,
      "64px",
    );

    // Adjust y to align to top-center
    const adjustedY = 32;

    setViewport({ x, y: adjustedY, zoom }, { duration: 500 });
  }, [nodes, setViewport, width, height]);
}
