import { useState } from "react";
import { useParams } from "react-router";

import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AttemptsService, QueryResultData } from "api";
import ExerciseDetails from "components/exercise/ExerciseDetails";
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
  const { exercise, attempt, setAttempt, updateText, submitAttempt } =
    useExercise(Number(exerciseId));

  const [tab, setTab] = useState<Tab>(Tab.Description);
  const [queryResult, setQueryResult] = useState<QueryResultData>();

  return (
    exercise && (
      <QueryPage
        databaseId={exercise.database.id}
        executeSubquery={AttemptsService.attemptsSubqueriesExecutionsCreate}
        fetchTree={AttemptsService.attemptsTreeRetrieve}
        query={attempt}
        queryResult={queryResult}
        setQueryResult={setQueryResult}
      >
        <div className="flex justify-between mx-3 mb-4">
          <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)}>
            <TabsList>
              <TabsTrigger value={Tab.Description}>Description</TabsTrigger>
              <TabsTrigger value={Tab.Editor}>Editor</TabsTrigger>
              <TabsTrigger value={Tab.Solution}>Solution</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button onClick={submitAttempt}>Submit</Button>
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
    )
  );
};

export default ExercisePage;
