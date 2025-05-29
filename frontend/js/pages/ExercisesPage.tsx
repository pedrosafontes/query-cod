import type { ColumnDef } from "@tanstack/react-table";
import { Check } from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router";

import { Badge } from "@/components/ui/badge";
import { ExercisesService, type ExerciseSummary } from "api";
import { DataTable } from "components/common/DataTable";
import DifficultyBadge from "components/exercise/DifficultyBadge";
import { useErrorToast } from "hooks/useErrorToast";

const ExercisesPage = () => {
  const [exercises, setExercises] = useState<ExerciseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useErrorToast();

  const fetchExercises = useCallback(async () => {
    try {
      const response = await ExercisesService.exercisesList();
      setExercises(response);
    } catch (error) {
      toast({
        title: "Error loading exercises",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExercises();
  }, [fetchExercises]);

  const columns: ColumnDef<ExerciseSummary>[] = [
    {
      accessorKey: "completed",
      header: "",
      cell: ({ row }) =>
        row.original.completed ? <Check className="text-green-600" /> : null,
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
    },
    {
      accessorKey: "difficulty",
      header: "Difficulty",
      cell: ({ row }) => (
        <DifficultyBadge difficulty={row.original.difficulty} />
      ),
    },
    {
      accessorKey: "database.name",
      header: "Database",
    },
  ];

  const navigate = useNavigate();

  const handleRowClick = (exercise: ExerciseSummary) => {
    navigate(`/exercises/${exercise.id}`);
  };

  return (
    <div className="p-6 h-screen overflow-auto">
      <h1 className="text-xl font-semibold mb-4">Exercises</h1>
      <DataTable
        columns={columns}
        data={exercises}
        loading={loading}
        onRowClick={handleRowClick}
      />
    </div>
  );
};

export default ExercisesPage;
