import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

interface GeneralErrorAlertProps {
  errors: { message: string }[];
  className?: string;
}

const GeneralErrorAlert = ({ errors, className }: GeneralErrorAlertProps) => {
  if (errors.length == 0) return null;

  return (
    <Alert variant="destructive" className={className}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Query validation failed</AlertTitle>
      <AlertDescription>
        <ul className="list-disc list-inside space-y-1">
          {errors.map((error, i) => (
            <li key={i}>{error.message}</li>
          ))}
        </ul>
      </AlertDescription>
    </Alert>
  );
};

export default GeneralErrorAlert;