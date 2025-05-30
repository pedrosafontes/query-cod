import { Repeat } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { QueriesService, Query } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type TranspileQueryButtonProps = {
  query?: Query;
  disabled: boolean;
  showFixErrorsTooltip: boolean;
  setQueryId: (queryId: number) => void;
  onSuccess?: () => void;
};

const TranspileQueryButton = ({
  query,
  disabled,
  showFixErrorsTooltip,
  setQueryId,
  onSuccess,
}: TranspileQueryButtonProps) => {
  const [isTranspiling, setIsTranspiling] = useState(false);
  const toast = useErrorToast();

  const transpileQuery = async (query: Query): Promise<void> => {
    setIsTranspiling(true);
    try {
      const transpiled = await QueriesService.queriesTranspileCreate({
        id: query.id,
      });

      setQueryId(transpiled.id);
      onSuccess?.();
    } catch (err) {
      toast({
        title: "Error transpiling query",
      });
    } finally {
      setIsTranspiling(false);
    }
  };

  return (
    <Tooltip delayDuration={200}>
      <TooltipTrigger asChild>
        <div>
          {" "}
          {/* div ensures tooltip is displayed when button is disabled */}
          <Button
            disabled={disabled || isTranspiling}
            size="sm"
            variant="secondary"
            onClick={query && (() => transpileQuery(query))}
          >
            {isTranspiling ? (
              <Spinner className="text-secondary-foreground" size="small" />
            ) : (
              <Repeat />
            )}
            Transpile
          </Button>
        </div>
      </TooltipTrigger>
      {showFixErrorsTooltip && (
        <TooltipContent side="left">
          Please fix the errors before transpiling the query.
        </TooltipContent>
      )}
    </Tooltip>
  );
};

export default TranspileQueryButton;
