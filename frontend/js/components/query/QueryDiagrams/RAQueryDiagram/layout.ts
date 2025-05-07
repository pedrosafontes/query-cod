import Dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@xyflow/react";

import "@xyflow/react/dist/style.css";

type getLayoutedNodesProps = {
  nodes: Node[];
  edges: Edge[];
};

const getLayoutedNodes = ({ nodes, edges }: getLayoutedNodesProps) => {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "TB" });

  const width = 256;
  const height = 48;

  nodes.forEach((node) => console.log(node.measured));

  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  nodes.forEach((node) =>
    g.setNode(node.id, {
      ...node,
      width: node.measured?.width ?? width,
      height: node.measured?.height ?? height,
    }),
  );

  Dagre.layout(g);

  return nodes.map((node) => {
    const position = g.node(node.id);
    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    const x = position.x - (node.measured?.width ?? width) / 2;
    const y = position.y - (node.measured?.height ?? height) / 2;

    return { ...node, position: { x, y } };
  });
};

export default getLayoutedNodes;
