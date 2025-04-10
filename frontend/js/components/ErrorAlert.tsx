import { AlertCircle } from "lucide-react";
import * as React from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ErrorAlertProps {
  title?: string;
  description?: React.ReactNode;
  className?: string;
}

const ErrorAlert = ({ title, description, className }: ErrorAlertProps) => {
  if (!title && !description) return null;

  return (
    <Alert className={className} variant="destructive">
      {title && (
        <>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{title}</AlertTitle>
        </>
      )}
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
};

export default ErrorAlert;
