import { AlertCircle } from "lucide-react";
import Markdown from "react-markdown";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ErrorAlertProps {
  title?: string;
  description?: string | null;
  className?: string;
}

const ErrorAlert = ({ title, description, className }: ErrorAlertProps) => {
  if (!title && !description) return null;

  return (
    <Alert className={`${className} p-3`} variant="destructive">
      {title && (
        <>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle className="text-sm">{title}</AlertTitle>
        </>
      )}
      {description && (
        <AlertDescription className="text-xs text-muted-foreground">
          <Markdown>{description}</Markdown>
        </AlertDescription>
      )}
    </Alert>
  );
};

export default ErrorAlert;
