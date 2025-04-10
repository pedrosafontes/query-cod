import { AlertCircle } from "lucide-react";

import { useToast } from "./use-toast";

export function useErrorToast() {
  const { toast } = useToast();

  return ({ title, description }: { title: string; description?: string }) =>
    toast({
      variant: "destructive",
      title: (
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
          <span>{title}</span>
        </div>
      ),
      description,
      duration: 3000,
    });
}
