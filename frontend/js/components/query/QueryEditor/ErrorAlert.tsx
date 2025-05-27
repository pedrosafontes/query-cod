import { AlertCircle, Info } from "lucide-react";
import Markdown from "marked-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { cn } from "lib/utils";

interface ErrorAlertProps {
  title?: string;
  description?: string;
  hint?: string;
  className?: string;
}

const ErrorAlert = ({
  title,
  description,
  hint,
  className,
}: ErrorAlertProps) => {
  if (!title && !description) return null;

  return (
    <Alert className={cn(className, "p-3")} variant="destructive">
      {title && (
        <>
          {!hint && <AlertCircle className="h-4 w-4" />}
          <AlertTitle className="text-sm">
            <Markdown>{title}</Markdown>
          </AlertTitle>
        </>
      )}
      {description && (
        <AlertDescription className="text-sm text-muted-foreground">
          <Markdown>{description}</Markdown>
        </AlertDescription>
      )}
      {hint && (
        <div className="mt-2 text-xs text-muted-foreground bg-muted py-2 px-3 rounded-md">
          <h3 className="font-semibold mb-1">
            <Info className="h-3 w-3 inline-block mr-1" />
            Hint
          </h3>
          <Markdown>{hint}</Markdown>
        </div>
      )}
    </Alert>
  );
};

export default ErrorAlert;
