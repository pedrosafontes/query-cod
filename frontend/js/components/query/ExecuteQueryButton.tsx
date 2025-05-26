import { Play } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { QueriesService, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type ExecuteQueryButtonProps = {
  queryId: number;
  disabled: boolean;
  hasErrors: boolean;
  setQueryResult: (result: QueryResultData | undefined) => void;
};

const ExecuteQueryButton = ({
  queryId,
  disabled,
  hasErrors,
  setQueryResult,
}: ExecuteQueryButtonProps) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const toast = useErrorToast();

  const executeQuery = async (): Promise<void> => {
    setIsExecuting(true);
    try {
      const execution = await QueriesService.queriesExecutionsCreate({
        id: queryId,
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
            disabled={disabled || isExecuting || hasErrors}
            size="sm"
            variant="default"
            onClick={executeQuery}
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
      {hasErrors && (
        <TooltipContent side="right">
          Please fix the errors before executing the query.
        </TooltipContent>
      )}
    </Tooltip>
  );
};

export default ExecuteQueryButton;
