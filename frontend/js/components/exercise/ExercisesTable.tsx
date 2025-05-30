import type { ColumnDef, ColumnFiltersState, Row } from "@tanstack/react-table";
import { Check, Filter } from "lucide-react";
import { useState, useEffect, Dispatch, SetStateAction } from "react";
import { useNavigate } from "react-router";

import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DifficultyEnum, LanguageEnum, type ExerciseSummary } from "api";
import { DataTable } from "components/common/DataTable";
import DifficultyBadge from "components/exercise/DifficultyBadge";
import { Button } from "components/ui/button";

interface ExercisesTableProps {
  exercises: ExerciseSummary[];
  loading: boolean;
}

const DEFAULT_LANGUAGE: LanguageEnum = "ra";
const DIFFICULTIES: DifficultyEnum[] = ["easy", "medium", "hard"];
const COMPLETION_STATUSES = [true, false];

const multiValueFilterFn = <TData,>(
  row: Row<TData>,
  columnId: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  filterValue: any[],
): boolean => {
  return filterValue.includes(row.getValue(columnId));
};

const ExercisesTable = ({ exercises, loading }: ExercisesTableProps) => {
  const [difficulties, setDifficulties] =
    useState<DifficultyEnum[]>(DIFFICULTIES);
  const [completionStatuses, setCompletionStatuses] =
    useState<boolean[]>(COMPLETION_STATUSES);
  const [language, setLanguage] = useState<LanguageEnum>(DEFAULT_LANGUAGE);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([
    {
      id: "language",
      value: DEFAULT_LANGUAGE,
    },
    {
      id: "difficulty",
      value: DIFFICULTIES,
    },
    {
      id: "completed",
      value: COMPLETION_STATUSES,
    },
  ]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateFilter = (id: string, value: any) => {
    setColumnFilters((prevFilters) => {
      const otherFilters = prevFilters.filter((filter) => filter.id !== id);
      return [...otherFilters, { id, value }];
    });
  };

  useEffect(() => updateFilter("language", language), [language]);
  useEffect(() => updateFilter("difficulty", difficulties), [difficulties]);
  useEffect(
    () => updateFilter("completed", completionStatuses),
    [completionStatuses],
  );

  const columns: ColumnDef<ExerciseSummary>[] = [
    {
      accessorKey: "completed",
      header: "",
      cell: ({ row }) =>
        row.original.completed ? <Check className="text-green-600" /> : null,
      filterFn: multiValueFilterFn,
    },
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      accessorKey: "language",
      header: "Language",
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.language.toUpperCase()}</Badge>
      ),
      filterFn: "equalsString",
    },
    {
      accessorKey: "difficulty",
      header: "Difficulty",
      cell: ({ row }) => (
        <DifficultyBadge difficulty={row.original.difficulty} />
      ),
      filterFn: multiValueFilterFn,
    },
    {
      accessorKey: "database.name",
      header: "Database",
    },
  ];

  const navigate = useNavigate();
  const handleRowClick = (exercise: ExerciseSummary) =>
    navigate(`/exercises/${exercise.id}`);

  return (
    <div>
      <ExerciseFilters
        completionStatuses={completionStatuses}
        difficulties={difficulties}
        language={language}
        setCompletionStatuses={setCompletionStatuses}
        setDifficulties={setDifficulties}
        setLanguage={setLanguage}
      />
      <DataTable
        columnFilters={columnFilters}
        columns={columns}
        data={exercises}
        loading={loading}
        onColumnFiltersChange={setColumnFilters}
        onRowClick={handleRowClick}
      />
    </div>
  );
};

interface ExerciseFiltersProps {
  language: LanguageEnum;
  setLanguage: Dispatch<SetStateAction<LanguageEnum>>;
  difficulties: DifficultyEnum[];
  setDifficulties: Dispatch<SetStateAction<DifficultyEnum[]>>;
  completionStatuses: boolean[];
  setCompletionStatuses: Dispatch<SetStateAction<boolean[]>>;
}

const ExerciseFilters = ({
  language,
  setLanguage,
  difficulties,
  setDifficulties,
  completionStatuses,
  setCompletionStatuses,
}: ExerciseFiltersProps) => {
  return (
    <div className="my-4 flex gap-4 items-center">
      <Tabs
        value={language}
        onValueChange={(v) => setLanguage(v as LanguageEnum)}
      >
        <TabsList>
          <TabsTrigger value="ra">Relational Algebra</TabsTrigger>
          <TabsTrigger value="sql">SQL</TabsTrigger>
        </TabsList>
      </Tabs>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button size="icon" variant="secondary">
            <Filter className="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56" side="right">
          <DropdownMenuLabel>Difficulty</DropdownMenuLabel>
          <DropdownMenuGroup>
            {DIFFICULTIES.map((difficulty) => (
              <DropdownMenuCheckboxItem
                key={difficulty}
                checked={difficulties.includes(difficulty)}
                className="capitalize"
                onCheckedChange={(checked) =>
                  setDifficulties((prev) =>
                    checked
                      ? [...prev, difficulty]
                      : prev.filter((d) => d !== difficulty),
                  )
                }
                onSelect={(event) => event.preventDefault()}
              >
                {difficulty}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuLabel>Completion</DropdownMenuLabel>
          <DropdownMenuGroup>
            <DropdownMenuCheckboxItem
              checked={completionStatuses.includes(false)}
              onCheckedChange={(checked) =>
                setCompletionStatuses((prev) =>
                  checked ? [...prev, false] : prev.filter((s) => s !== false),
                )
              }
              onSelect={(event) => event.preventDefault()}
            >
              To-do
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem
              checked={completionStatuses.includes(true)}
              onCheckedChange={(checked) =>
                setCompletionStatuses((prev) =>
                  checked ? [...prev, true] : prev.filter((s) => s !== true),
                )
              }
              onSelect={(event) => event.preventDefault()}
            >
              Completed
            </DropdownMenuCheckboxItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default ExercisesTable;
