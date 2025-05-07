import {
  ReactFlow,
  Background,
  Controls,
  Panel,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import type { Edge, Node } from "@xyflow/react";
import React, { useEffect, useState } from "react";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RATree } from "api";
import "@xyflow/react/dist/style.css";
import SchemaDiagramNode from "components/database/SchemaNode";
import useSchemaDiagram from "components/database/useSchemaDiagram";
import useLayout from "hooks/useLayout";
import { useTopCenterFitView } from "hooks/useTopCenterView";

import RADiagramNode from "./RAQueryDiagram/RANode";
import useRAQueryDiagram from "./RAQueryDiagram/useRAQueryDiagram";

export type QueryDiagramsProps = {
  databaseId: number;
  tree?: RATree;
  children?: React.ReactNode;
};

const nodeTypes = {
  table: SchemaDiagramNode,
  ra: RADiagramNode,
};

type DigramEnum = "schema" | "query";

const QueryDiagrams = ({ databaseId, tree, children }: QueryDiagramsProps) => {
  const [diagram, setDiagram] = useState<DigramEnum>("schema");
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const {
    nodes: schemaNodes,
    edges: schemaEdges,
    layout: schemaLayout,
  } = useSchemaDiagram({
    databaseId,
  });
  const {
    nodes: queryNodes,
    edges: queryEdges,
    layout: queryLayout,
  } = useRAQueryDiagram({ tree });

  const layout = diagram === "schema" ? schemaLayout : queryLayout;

  useEffect(() => {
    if (diagram === "schema") {
      setEdges(schemaEdges);
      setNodes(schemaNodes);
    } else {
      setEdges(queryEdges);
      setNodes(queryNodes);
    }
  }, [
    diagram,
    schemaNodes,
    schemaEdges,
    queryNodes,
    queryEdges,
    setNodes,
    setEdges,
  ]);

  useLayout({ layout });
  useTopCenterFitView(nodes);

  return (
    <ReactFlow
      edges={edges}
      nodeTypes={nodeTypes}
      nodes={nodes}
      onEdgesChange={onEdgesChange}
      onNodesChange={onNodesChange}
    >
      <Panel position="top-right">
        <Tabs
          value={diagram}
          onValueChange={(value) => setDiagram(value as DigramEnum)}
        >
          <TabsList>
            <TabsTrigger value="schema">Schema</TabsTrigger>
            <TabsTrigger value="query">Query</TabsTrigger>
          </TabsList>
        </Tabs>
      </Panel>
      <Background />
      <Controls position="top-left" />
      <Panel className="w-full pb-2 pr-8" position="bottom-left">
        {children}
      </Panel>
    </ReactFlow>
  );
};

export default QueryDiagrams;
