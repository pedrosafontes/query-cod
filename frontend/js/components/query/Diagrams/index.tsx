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
import { Query, QueryResultData } from "api";
import "@xyflow/react/dist/style.css";
import SchemaDiagramNode from "components/database/SchemaNode";
import useSchemaDiagram from "components/database/useSchemaDiagram";
import { useTopCenterFitView } from "hooks/useTopCenterView";

import RADiagramNode from "./QueryDiagram/RAQueryDiagram/RANode";
import SQLDiagramNode from "./QueryDiagram/SQLQueryDiagram/SQLNode";
import useQueryDiagram from "./QueryDiagram/useQueryDiagram";

export type DiagramsProps = {
  databaseId: number;
  query?: Query;
  setQueryResult: (result?: QueryResultData) => void;
  children?: React.ReactNode;
};

const nodeTypes = {
  table: SchemaDiagramNode,
  ra: RADiagramNode,
  sql: SQLDiagramNode,
};

type DigramEnum = "schema" | "query";

const Diagrams = ({
  databaseId,
  query,
  setQueryResult,
  children,
}: DiagramsProps) => {
  const [diagram, setDiagram] = useState<DigramEnum>("schema");
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const { nodes: schemaNodes, edges: schemaEdges } = useSchemaDiagram({
    databaseId,
  });
  const { nodes: queryNodes, edges: queryEdges } = useQueryDiagram({
    query,
    setQueryResult,
  });

  useEffect(() => {
    if (diagram !== "schema") return;
    console.log("Setting up schema diagram.");
    setNodes(schemaNodes);
    setEdges(schemaEdges);
  }, [diagram, schemaNodes, schemaEdges, setNodes, setEdges]);
  
  useEffect(() => {
    if (diagram !== "query") return;
    console.log("Setting up query diagram.");
    setNodes(queryNodes);
    setEdges(queryEdges);
  }, [diagram, queryNodes, queryEdges, setNodes, setEdges]);

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
          className="shadow rounded"
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
      <Controls
        className="shadow rounded overflow-hidden"
        orientation="horizontal"
        position="top-left"
        showInteractive={false}
      />
      <Panel className="w-full pb-2 pr-8" position="bottom-left">
        {children}
      </Panel>
    </ReactFlow>
  );
};

export default Diagrams;
