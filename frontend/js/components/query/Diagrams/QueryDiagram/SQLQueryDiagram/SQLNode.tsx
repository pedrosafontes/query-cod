import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import {
  SquarePen,
  CircleHelp,
  Filter,
  Group,
  Merge,
  List,
  type LucideIcon,
  SortAsc,
  Table,
  SquaresUnite,
  SquaresIntersect,
  SquaresSubtract,
  SquaresExclude,
} from "lucide-react";
import { ReactNode } from "react";
import Markdown from "react-markdown";

import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import {
  QueryResultData,
  SQLTree,
  TableNode,
  AliasNode,
  SQLJoinNode,
  SetOpNode,
  SelectNode,
  WhereNode,
  GroupByNode,
  HavingNode,
  OrderByNode,
  QueryError,
} from "api";
import { cn } from "lib/utils";

import useExecuteSubquery from "../useExecuteSubquery";

export type SQLNodeData = {
  id: number;
  queryId: number;
  setQueryResult: (result?: QueryResultData) => void;
  errors: QueryError[];
} & Omit<SQLTree, "children" | "validation_errors">;

export type SQLNode = Node<SQLNodeData, "sql">;

const SQLDiagramNode = ({ data }: NodeProps<SQLNode>) => {
  const {
    queryId,
    id,
    setQueryResult,
    sql_node_type: type,
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
    icon: LucideIcon;
    title?: string;
    hoverContent?: ReactNode;
    borderClass?: string;
    bgClass?: string;
  } => {
    switch (type) {
      case "Table": {
        const { name } = props as TableNode;
        return {
          icon: Table,
          title: name,
        };
      }
      case "Alias": {
        const { alias } = props as AliasNode;
        return {
          icon: SquarePen,
          title: `AS ${alias}`,
          borderClass: "border-gray-300",
          bgClass: "bg-gray-50",
        };
      }
      case "Join": {
        const { method } = props as SQLJoinNode;
        return {
          icon: Merge,
          title: `${method} JOIN`,
          borderClass: "border-pink-300",
          bgClass: "bg-pink-50",
        };
      }
      case "Select": {
        const { columns } = props as SelectNode;
        const hoverContent = (
          <>
            <h3>Attributes</h3>
            <ul className="list-disc pl-3">
              {columns.map((column) => (
                <li key={column}>
                  <span className="text-muted-foreground">{column}</span>
                </li>
              ))}
            </ul>
          </>
        );
        return {
          icon: List,
          title: "SELECT",
          hoverContent,
          borderClass: "border-blue-300",
          bgClass: "bg-blue-50",
        };
      }
      case "Where": {
        const { condition } = props as WhereNode;
        const hoverContent = (
          <>
            <h3>Condition</h3>
            <Markdown>{`\`\`\`${condition}\`\`\``}</Markdown>
          </>
        );
        return {
          icon: Filter,
          title: "WHERE",
          hoverContent,
          borderClass: "border-orange-300",
          bgClass: "bg-orange-50",
        };
      }
      case "GroupBy": {
        const { keys } = props as GroupByNode;
        const hoverContent = (
          <>
            <h3>Fields</h3>
            <ul className="list-disc pl-3">
              {keys.map((key) => (
                <li key={key}>
                  <span className="text-muted-foreground">{key}</span>
                </li>
              ))}
            </ul>
          </>
        );
        return {
          icon: Group,
          title: "GROUP BY",
          hoverContent,
          borderClass: "border-green-300",
          bgClass: "bg-green-50",
        };
      }
      case "Having": {
        const { condition } = props as HavingNode;
        const hoverContent = (
          <>
            <h3>Condition</h3>
            <Markdown>{`\`\`\`${condition}\`\`\``}</Markdown>
          </>
        );
        return {
          icon: Filter,
          title: "HAVING",
          hoverContent,
          borderClass: "border-orange-300",
          bgClass: "bg-orange-50",
        };
      }
      case "OrderBy": {
        const { keys } = props as OrderByNode;
        const hoverContent = (
          <>
            <h3>Fields</h3>
            <ul className="list-disc pl-3">
              {keys.map((key) => (
                <li key={key}>
                  <span className="text-muted-foreground">{key}</span>
                </li>
              ))}
            </ul>
          </>
        );
        return {
          icon: SortAsc,
          title: "ORDER BY",
          hoverContent,
          borderClass: "border-purple-300",
          bgClass: "bg-purple-50",
        };
      }
      case "SetOp": {
        const { operator } = props as SetOpNode;
        let icon: LucideIcon;
        const borderClass = "border-yellow-300";
        const bgClass = "bg-yellow-50";

        switch (operator) {
          case "union":
            icon = SquaresUnite;
            break;
          case "intersect":
            icon = SquaresIntersect;
            break;
          case "except":
            icon = SquaresSubtract;
            break;
          default:
            icon = SquaresExclude;
        }
        return {
          icon,
          title: operator.toUpperCase(),
          borderClass,
          bgClass,
        };
      }
      default:
        return {
          icon: CircleHelp,
        };
    }
  };

  const {
    icon: Icon,
    title,
    hoverContent,
    borderClass,
    bgClass,
  } = getConfiguration();

  return (
    <HoverCard>
      <HoverCardTrigger asChild>
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
          <Icon /> {title}
          <Handle
            className="invisible size-0 border-0 bottom-1"
            position={Position.Bottom}
            type="target"
          />
        </Button>
      </HoverCardTrigger>
      {hoverContent && (
        <HoverCardContent className="text-xs p-2" side="right">
          {hoverContent}
        </HoverCardContent>
      )}
    </HoverCard>
  );
};

export default SQLDiagramNode;
