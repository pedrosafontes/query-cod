import type { ColumnDef } from "@tanstack/react-table";
import { useEffect } from "react";

import { useToast } from "@/hooks/use-toast";
import { QueryResultData } from "js/api";

import { DataTable } from "./DataTable";

const QueryResult = ({
  success,
  result,
}: {
  success: boolean;
  result: QueryResultData | undefined;
}) => {
  const { toast } = useToast();

  useEffect(() => {
    if (!success) {
      toast({ description: "Query execution failed." });
    } else if (result && result.columns.length === 0) {
      toast({ description: "No results found." });
    }
  }, [success, result, toast]);

  if (!success || !result || result.columns.length === 0) {
    return null;
  }

  const columns: ColumnDef<Record<string, string | null>>[] =
    result.columns.map((col) => ({
      accessorKey: col,
      header: col,
    }));

  const data = result.rows.map((row) =>
    Object.fromEntries(row.map((cell, i) => [result.columns[i], cell])),
  );

  return (
    <div className="[&_table]:text-xs [&_td]:px-3 [&_td]:py-2 [&_th]:px-3 [&_th]:py-2 [&_th]:h-auto">
      <DataTable columns={columns} data={data} pageSize={5} />
    </div>
  );
};

export default QueryResult;
