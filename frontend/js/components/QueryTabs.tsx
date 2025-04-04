// components/QueryTabs.tsx
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type QueryTabsProps = {
  queries: { id: number }[];
  currentQueryId?: string;
  onSelect: (id: string) => void;
  onCreate: () => void;
};

export default function QueryTabs({
  queries,
  currentQueryId,
  onSelect,
  onCreate,
}: QueryTabsProps) {
  useEffect(() => {
    if (!currentQueryId && queries.length > 0) {
      onSelect(queries[0].id.toString());
    }
  }, [queries, currentQueryId, onSelect]);

  return (
    <div className="flex flex-col h-full">
      <div className="mb-3 px-2">
        <Button
          className="w-full"
          size="sm"
          variant="outline"
          onClick={onCreate}
        >
          New Query
        </Button>
      </div>

      <div className="overflow-y-auto flex-1 px-2">
        <div className="flex flex-col gap-1">
          {queries.map((query) => (
            <Button
              key={query.id}
              className={cn(
                "w-full justify-start",
                currentQueryId === query.id.toString() ? "bg-gray-100" : "",
              )}
              size="sm"
              variant="ghost"
              onClick={() => onSelect(query.id.toString())}
            >
              Query {query.id}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
