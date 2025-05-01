import { AlertTriangle, CheckCircle } from "lucide-react";

import { Spinner } from "@/components/ui/spinner";
import { Status } from "hooks/useAutosave";

type AutosaveStatusProps = {
  status: Status;
};

const AutosaveStatus = ({ status }: AutosaveStatusProps) => {
  if (status === "saving") {
    return (
      <span className="inline-flex items-center gap-1 text-gray-400 animate-pulse">
        <Spinner size="xs" />
        Saving...
      </span>
    );
  }

  if (status === "error") {
    return (
      <span className="inline-flex items-center gap-1 text-destructive">
        <AlertTriangle className="h-3 w-3" />
        Error saving
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 text-green-600">
      <CheckCircle className="h-3 w-3" />
      Saved
    </span>
  );
};

export default AutosaveStatus;
