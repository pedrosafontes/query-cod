import { Play } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { QueriesService, Query, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type ExecuteQueryButtonProps = {
  query?: Query;
  disabled: boolean;
  showFixErrorsTooltip: boolean;
  setQueryResult: (result?: QueryResultData) => void;
};

const ExecuteQueryButton = ({
  query,
  disabled,
  showFixErrorsTooltip,
  setQueryResult,
}: ExecuteQueryButtonProps) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const toast = useErrorToast();

  const executeQuery = async (query: Query): Promise<void> => {
    setIsExecuting(true);
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: query.id,
      });

      setQueryResult(execution.results);
    } catch (err) {
      toast({
        title: "Error executing query",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <Tooltip delayDuration={200}>
      <TooltipTrigger asChild>
        <div>
          {" "}
          {/* div ensures tooltip is displayed when button is disabled */}
          <Button
            disabled={disabled || isExecuting}
            size="sm"
            variant="default"
            onClick={query && (() => executeQuery(query))}
          >
            {isExecuting ? (
              <Spinner className="text-primary-foreground" size="small" />
            ) : (
              <Play />
            )}
            Execute
          </Button>
        </div>
      </TooltipTrigger>
      {showFixErrorsTooltip && (
        <TooltipContent side="right">
          Please fix the errors before executing the query.
        </TooltipContent>
      )}
    </Tooltip>
  );
};

export default ExecuteQueryButton;
