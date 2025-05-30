import type { ColumnFiltersState, ColumnDef } from "@tanstack/react-table";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Dispatch, SetStateAction } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "lib/utils";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  pageSize?: number | null; // null or undefined disables pagination
  loading?: boolean;
  cellClassName?: string;
  onRowClick?: (row: TData) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: Dispatch<SetStateAction<ColumnFiltersState>>;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  pageSize,
  loading,
  cellClassName,
  onRowClick,
  columnFilters,
  onColumnFiltersChange,
}: DataTableProps<TData, TValue>) {
  const paginationEnabled = !!pageSize;

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    state: {
      columnFilters,
    },
    onColumnFiltersChange,
    getFilteredRowModel: getFilteredRowModel(),
    ...(paginationEnabled && {
      getPaginationRowModel: getPaginationRowModel(),
    }),
    initialState: paginationEnabled
      ? {
          pagination: {
            pageSize,
          },
        }
      : {},
  });

  const { rows } = table.getRowModel();

  return (
    <div>
      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {rows.length ? (
              rows.map((row) => (
                <TableRow
                  key={row.id}
                  className={cn(
                    onRowClick && "cursor-pointer",
                    "hover:bg-muted",
                  )}
                  data-state={row.getIsSelected() && "selected"}
                  onClick={(e) => {
                    const target = e.target as HTMLElement;
                    if (target.closest("button, a")) return;
                    onRowClick?.(row.original);
                  }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className={cellClassName}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  className="h-24 text-center"
                  colSpan={columns.length}
                >
                  {loading ? <Spinner size="small" /> : "No results."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {paginationEnabled && (
        <div className="flex items-center justify-end space-x-2 pt-4">
          <Button
            disabled={!table.getCanPreviousPage()}
            size="sm"
            variant="outline"
            onClick={() => table.previousPage()}
          >
            Previous
          </Button>
          <Button
            disabled={!table.getCanNextPage()}
            size="sm"
            variant="outline"
            onClick={() => table.nextPage()}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
