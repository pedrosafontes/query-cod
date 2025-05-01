import { Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type ExecuteQueryButtonProps = {
  disabled: boolean;
  loading: boolean;
  hasErrors: boolean;
  handleExecuteQuery: () => Promise<void>;
};

const ExecuteQueryButton = ({
  disabled,
  loading,
  hasErrors,
  handleExecuteQuery,
}: ExecuteQueryButtonProps) => {
  return (
    <Tooltip delayDuration={200}>
      <TooltipTrigger asChild>
        <div>
          <Button
            disabled={disabled}
            size="sm"
            variant="default"
            onClick={handleExecuteQuery}
          >
            {loading ? (
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
