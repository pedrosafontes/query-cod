import type { ColumnDef } from "@tanstack/react-table";

import { Skeleton } from "@/components/ui/skeleton";

import { QueryResultData } from "../../api";
import { DataTable } from "../common/DataTable";

type QueryResultProps = {
  result: QueryResultData;
};

const QueryResult = ({ result }: QueryResultProps) => {
  if (result.columns.length === 0) {
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
      <DataTable
        cellClassName="text-nowrap"
        columns={columns}
        data={data}
        pageSize={5}
      />
    </div>
  );
};

export default QueryResult;
