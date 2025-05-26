import { Repeat } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { QueriesService } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type TranspileQueryButtonProps = {
  queryId: number;
  disabled: boolean;
  hasErrors: boolean;
  setQueryId: (queryId: number) => void;
  onSuccess?: () => void;
};

const TranspileQueryButton = ({
  queryId,
  disabled,
  hasErrors,
  setQueryId,
  onSuccess,
}: TranspileQueryButtonProps) => {
  const [isTranspiling, setIsTranspiling] = useState(false);
  const toast = useErrorToast();

  const transpileQuery = async (): Promise<void> => {
    setIsTranspiling(true);
    try {
      const transpiled = await QueriesService.queriesTranspileCreate({
        id: queryId,
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
            disabled={disabled || isTranspiling || hasErrors}
            size="sm"
            variant="secondary"
            onClick={transpileQuery}
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
      {hasErrors && (
        <TooltipContent side="left">
          Please fix the errors before transpiling the query.
        </TooltipContent>
      )}
    </Tooltip>
  );
};

export default TranspileQueryButton;
