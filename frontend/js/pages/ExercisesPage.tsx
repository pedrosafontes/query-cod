import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router";

import { Badge } from "@/components/ui/badge";
import { DifficultyEnum, ExercisesService, type ExerciseSummary } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import { DataTable } from "../components/common/DataTable";

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
      cell: ({ row }) => renderDifficultyBadge(row.original.difficulty),
    },
    {
      accessorKey: "database.name",
      header: "Database",
    },
  ];

  const renderDifficultyBadge = (difficulty: DifficultyEnum) => {
    let className: string;

    switch (difficulty) {
      case "easy":
        className = "bg-green-100 text-green-800";
        break;
      case "medium":
        className = "bg-yellow-100 text-yellow-800";
        break;
      case "hard":
        className = "bg-red-100 text-red-800";
        break;
      default:
        className = "bg-gray-100 text-gray-800";
    }

    return <Badge className={className}>{difficulty}</Badge>;
  };

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
