import { type Edge, type Node } from "@xyflow/react";
import ELK from "elkjs/lib/elk.bundled";

import { type SchemaNode } from "./SchemaNode";

// elk layouting options can be found here:
// https://www.eclipse.org/elk/reference/algorithms/org-eclipse-elk-layered.html
const layoutOptions = {
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",
  "elk.layered.spacing.edgeNodeBetweenLayers": "40",
  "elk.spacing.nodeNode": "40",
  "elk.layered.nodePlacement.strategy": "SIMPLE",
};

const elk = new ELK();

type getLayoutedNodesProps = {
  nodes: Node[];
  edges: Edge[];
};

// uses elkjs to give each node a layouted position
const getLayoutedNodes = async ({
  nodes,
  edges,
}: getLayoutedNodesProps): Promise<Node[]> => {
  const graph = {
    id: "root",
    layoutOptions,
    children: (nodes as SchemaNode[]).map((n) => {
      const cols = Object.keys(n.data.fields);
      const targetPorts = cols.map((col) => ({
        id: `${n.data.table}.${col}`,

        // ⚠️ it's important to let elk know on which side the port is
        // in this example targets are on the left (WEST) and sources on the right (EAST)
        properties: {
          side: "WEST",
        },
      }));

      const sourcePorts = cols.map((col) => ({
        id: `${n.data.table}.${col}`,
        properties: {
          side: "EAST",
        },
      }));

      return {
        id: n.id,
        width: n.measured?.width ?? 192,
        height: n.measured?.height ?? (cols.length + 1) * 32,
        // ⚠️ we need to tell elk that the ports are fixed, in order to reduce edge crossings
        properties: {
          "org.eclipse.elk.portConstraints": "FIXED_ORDER",
        },
        // we are also passing the id, so we can also handle edges without a sourceHandle or targetHandle option
        ports: [{ id: n.id }, ...targetPorts, ...sourcePorts],
      };
    }),
    edges: edges.map((e) => ({
      id: e.id,
      sources: [e.sourceHandle || e.source],
      targets: [e.targetHandle || e.target],
    })),
  };

  const layoutedGraph = await elk.layout(graph);

  const layoutedNodes = nodes.map((node) => {
    const layoutedNode = layoutedGraph.children?.find(
      (lgNode) => lgNode.id === node.id,
    );

    return {
      ...node,
      position: {
        x: layoutedNode?.x ?? 0,
        y: layoutedNode?.y ?? 0,
      },
    };
  });

  return layoutedNodes;
};

export default getLayoutedNodes;
