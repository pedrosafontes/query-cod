import { useEffect, useState, useCallback } from "react";

import { ExercisesService, type ExerciseSummary } from "api";
import ExercisesTable from "components/exercise/ExercisesTable";
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
      toast({ title: "Error loading exercises" });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchExercises();
  }, [fetchExercises]);

  return (
    <div className="p-6 h-screen overflow-auto">
      <h1 className="text-xl font-semibold">Exercises</h1>
      <ExercisesTable exercises={exercises} loading={loading} />
    </div>
  );
};

export default ExercisesPage;
