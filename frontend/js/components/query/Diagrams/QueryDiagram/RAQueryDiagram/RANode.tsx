import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { Button } from "@/components/ui/button";
import {
  GroupedAggregationNode,
  ProjectionNode,
  QueryError,
  QueryResultData,
  RAJoinNode,
  RATree,
  RelationNode,
  RenameNode,
  SelectionNode,
  SetOperationNode,
  ThetaJoinNode,
  TopNNode,
} from "api";
import LatexFormula from "components/query/QueryEditor/RAEditor/LatexFormula";
import { cn } from "lib/utils";

import useExecuteSubquery from "../useExecuteSubquery";

export type RANodeData = {
  id: number;
  queryId: number;
  setQueryResult: (result?: QueryResultData) => void;
  errors: QueryError[];
} & Omit<RATree, "children" | "validation_errors">;
export type RANode = Node<RANodeData, "ra">;

const RADiagramNode = ({ data }: NodeProps<RANode>) => {
  const {
    queryId,
    id,
    setQueryResult,
    ra_node_type: type,
    errors,
    ...props
  } = data;
  const { isExecuting, executeSubquery } = useExecuteSubquery({
    queryId,
    subqueryId: id,
    setQueryResult,
  });

  const isExecutable = errors.length === 0;

  const getConfiguration = (): {
    latex?: string;
    borderClass?: string;
    bgClass?: string;
  } => {
    switch (type) {
      case "Relation": {
        const { name } = props as RelationNode;
        return {
          latex: `\\text{${name}}`,
        };
      }
      case "Projection": {
        const { attributes } = props as ProjectionNode;
        return {
          latex: `\\pi_{${attributes.join(", ")}}`,
          borderClass: "border-blue-300",
          bgClass: "bg-blue-50",
        };
      }
      case "Selection": {
        const { condition } = props as SelectionNode;
        return {
          latex: `\\sigma_{${condition}}`,
          borderClass: "border-orange-300",
          bgClass: "bg-orange-50",
        };
      }
      case "Rename": {
        const { alias } = props as RenameNode;
        return {
          latex: `\\rho_{${alias}}`,
          borderClass: "border-gray-300",
          bgClass: "bg-gray-50",
        }
      }
      case "Division": {
        return {
          latex: `\\div`,
          borderClass: "border-purple-300",
          bgClass: "bg-purple-50",
        };
      }
      case "SetOperation": {
        const { operator } = props as SetOperationNode;
        let latex: string | undefined;
        let borderClass = "border-yellow-300";
        let bgClass = "bg-yellow-50";
        switch (operator) {
          case "UNION":
            latex = `\\cup`;
            break;
          case "INTERSECT":
            latex = `\\cap`;
            break;
          case "DIFFERENCE":
            latex = `-`;
            break;
          case "CARTESIAN":
            latex = `\\times`;
            borderClass = "border-pink-300";
            bgClass = "bg-pink-50";
            break;
          default:
            break;
        }
        return {
          latex,
          borderClass,
          bgClass,
        };
      }
      case "Join": {
        const { operator } = props as RAJoinNode;
        return {
          latex: operator === "SEMI" ? `\\ltimes` : `\\Join`,
          borderClass: "border-pink-300",
          bgClass: "bg-pink-50",
        };
      }
      case "ThetaJoin": {
        const { condition } = props as ThetaJoinNode;
        return {
          latex: `\\overset{${condition}}{\\bowtie}`,
          borderClass: "border-pink-300",
          bgClass: "bg-pink-50",
        };
      }
      case "GroupedAggregation": {
        const { group_by: groupBy, aggregations } =
          props as GroupedAggregationNode;
        const groupByLatex = groupBy.join(", ");
        const aggregationsLatex = aggregations
          .map((aggregation) => `(${aggregation.join(", ")})`)
          .join(", ");
        return {
          latex: `\\Gamma_{(${groupByLatex})(${aggregationsLatex})}`,
          borderClass: "border-teal-300",
          bgClass: "bg-teal-50",
        };
      }
      case "TopN": {
        const { limit, attribute } = props as TopNNode;
        return {
          latex: `\\operatorname{T}_(${limit}, ${attribute})`,
          borderClass: "border-purple-300",
          bgClass: "bg-purple-50",
        };
      }
      default:
        return {};
    }
  };

  const { latex, borderClass, bgClass } = getConfiguration();

  return (
    <Button
      className={cn(
        "border transition-colors",
        borderClass ?? "border",
        bgClass ?? "bg-white",
        isExecuting &&
          "cursor-wait animate-[pulse-scale_1s_ease-in-out_infinite]",
      )}
      disabled={!isExecutable}
      variant="ghost"
      onClick={executeSubquery}
    >
      <Handle
        className="invisible size-0 border-0 top-1"
        position={Position.Top}
        type="source"
      />
      <LatexFormula expression={latex || "?"} />
      <Handle
        className="invisible size-0 border-0 bottom-1"
        position={Position.Bottom}
        type="target"
      />
    </Button>
  );
};

export default RADiagramNode;
