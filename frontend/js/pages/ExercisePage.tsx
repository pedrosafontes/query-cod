import { useState } from "react";
import { useParams } from "react-router";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AttemptsService, QueryResultData } from "api";
import ExerciseDetails from "components/exercise/ExerciseDetails";
import SubmitAttemptButton from "components/exercise/SubmitAttemptButton";
import { useExercise } from "components/exercise/useExercise";
import QueryEditor from "components/query/QueryEditor";
import QueryPage from "components/query/QueryPage";
import ReadOnlyQuery from "components/query/ReadOnlyQuery";

enum Tab {
  Description = "description",
  Editor = "editor",
  Solution = "solution",
}

const ExercisePage = () => {
  const { exerciseId } = useParams<{ exerciseId: string }>();
  const { exercise, attempt, setAttempt, updateText } = useExercise(
    Number(exerciseId),
  );

  const [tab, setTab] = useState<Tab>(Tab.Description);
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [confirmRevealSolution, setConfirmRevealSolution] = useState(false);

  const handleTabChange = (value: string) => {
    const tab = value as Tab;
    if (tab === Tab.Solution && attempt && !attempt.completed) {
      setConfirmRevealSolution(true);
    } else {
      setTab(tab);
    }
  };

  const revealSolution = () => {
    setTab(Tab.Solution);
    setConfirmRevealSolution(false);
  };

  return (
    exercise && (
      <>
        <QueryPage
          databaseId={exercise.database.id}
          executeSubquery={AttemptsService.attemptsSubqueriesExecutionsCreate}
          fetchTree={AttemptsService.attemptsTreeRetrieve}
          query={attempt}
          queryResult={queryResult}
          setQueryResult={setQueryResult}
        >
          <div className="flex justify-between mx-3 mb-4">
            <Tabs value={tab} onValueChange={handleTabChange}>
              <TabsList>
                <TabsTrigger value={Tab.Description}>Description</TabsTrigger>
                <TabsTrigger value={Tab.Editor}>Editor</TabsTrigger>
                <TabsTrigger value={Tab.Solution}>Solution</TabsTrigger>
              </TabsList>
            </Tabs>
            <SubmitAttemptButton attempt={attempt} />
          </div>
          {tab === Tab.Description && (
            <ExerciseDetails className="mx-3" exercise={exercise} />
          )}
          {tab === Tab.Editor && attempt && (
            <QueryEditor
              query={attempt}
              setQuery={setAttempt}
              updateText={updateText}
            />
          )}
          {tab === Tab.Solution && (
            <ReadOnlyQuery
              language={exercise.language}
              text={exercise.solution}
            />
          )}
        </QueryPage>

        <Dialog
          open={confirmRevealSolution}
          onOpenChange={setConfirmRevealSolution}
        >
          <DialogContent>
            <div className="space-y-4">
              <h2 className="font-semibold">You are almost there!</h2>
              <p className="text-sm text-muted-foreground">
                Viewing the solution now may reduce your opportunity to practice
                solving the problem independently. Are you sure you want to
                continue?
              </p>
            </div>
            <DialogFooter>
              <Button
                variant="secondary"
                onClick={() => setConfirmRevealSolution(false)}
              >
                Cancel
              </Button>
              <Button onClick={revealSolution}>Reveal Solution</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </>
    )
  );
};

export default ExercisePage;
