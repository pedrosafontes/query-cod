import { AlertCircle, Info } from "lucide-react";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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
    <Alert className={`${className} p-3`} variant="destructive">
      {title && (
        <>
          {!hint && <AlertCircle className="h-4 w-4" />}
          <AlertTitle className="text-sm">{title}</AlertTitle>
        </>
      )}
      {description && (
        <AlertDescription className="text-sm text-muted-foreground">
          <Markdown rehypePlugins={[rehypeRaw]}>{description}</Markdown>
        </AlertDescription>
      )}
      {hint && (
        <div className="mt-2 text-xs text-muted-foreground bg-muted py-2 px-3 rounded-md">
          <h3 className="font-semibold mb-1">
            <Info className="h-3 w-3 inline-block mr-1" />
            Hint
          </h3>
          <div className="italic">
            <Markdown rehypePlugins={[rehypeRaw]}>{hint}</Markdown>
          </div>
        </div>
      )}
    </Alert>
  );
};

export default ErrorAlert;
