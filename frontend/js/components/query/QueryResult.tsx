import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useState } from "react";

import { cn } from "lib/utils";

import { QueryResultData } from "../../api";
import { DataTable } from "../common/DataTable";
import { Button } from "../ui/button";

type QueryResultProps = {
  className?: string;
  result: QueryResultData;
  pageSize?: number;
};

const QueryResult = ({ result, pageSize = 5, className }: QueryResultProps) => {
  const [closed, setClosed] = useState(false);
  useEffect(() => {
    setClosed(false);
  }, [result]);

  if (result.columns.length === 0 || closed) {
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
    <div
      className={cn(
        className,
        "[&_table]:text-xs [&_td]:px-3 [&_td]:py-2 [&_th]:px-3 [&_th]:py-2 [&_th]:h-auto relative",
      )}
    >
      <DataTable
        key={result.columns.join()}
        cellClassName="text-nowrap"
        columns={columns}
        data={data}
        pageSize={pageSize}
      />
      <Button
        className="absolute bottom-0 left-0"
        size="sm"
        variant="outline"
        onClick={() => setClosed(true)}
      >
        Close
      </Button>
    </div>
  );
};

export default QueryResult;
