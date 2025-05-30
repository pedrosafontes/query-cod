import { useEffect, useState } from "react";

import { Attempt, AttemptsService, Exercise, ExercisesService } from "api";
import { useErrorToast } from "hooks/useErrorToast";

export const useExercise = (exerciseId: number) => {
  const [exercise, setExercise] = useState<Exercise>();
  const [attempt, setAttempt] = useState<Attempt>();
  const toast = useErrorToast();

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        const result = await ExercisesService.exercisesRetrieve({
          id: exerciseId,
        });
        setExercise(result);
        setAttempt(result.attempt);
      } catch {
        toast({ title: "Error loading exercise" });
      }
    };
    fetchExercise();
  }, [exerciseId]);

  const updateText = async (value: string) => {
    if (!attempt) return;
    const updated = await AttemptsService.attemptsPartialUpdate({
      id: attempt.id,
      requestBody: { text: value },
    });
    setAttempt(updated);
  };

  return { exercise, attempt, setAttempt, updateText };
};
