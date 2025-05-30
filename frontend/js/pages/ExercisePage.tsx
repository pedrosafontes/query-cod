import Markdown from "marked-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Attempt,
  AttemptsService,
  ExercisesService,
  QueryResultData,
} from "api";
import DifficultyBadge from "components/exercise/DifficultyBadge";
import QueryEditor from "components/query/QueryEditor";
import CodeEditor from "components/query/QueryEditor/CodeEditor";
import LatexFormula from "components/query/QueryEditor/RAEditor/LatexFormula";
import QueryPage from "components/query/QueryPage";
import { useErrorToast } from "hooks/useErrorToast";

type Tab = "description" | "editor" | "solution";

const ExercisePage = () => {
  const [queryResult, setQueryResult] = useState<QueryResultData>();
  const [tab, setTab] = useState<Tab>("description");
  const { exerciseId: exerciseParamId } = useParams<{ exerciseId: string }>();
  const [exercise, setExercise] =
    useState<Awaited<ReturnType<typeof ExercisesService.exercisesRetrieve>>>();
  const [attempt, setAttempt] = useState<Attempt>();
  const toast = useErrorToast();

  const exerciseId = Number(exerciseParamId);

  const fetchExercise = async () => {
    try {
      const result = await ExercisesService.exercisesRetrieve({
        id: exerciseId,
      });
      setExercise(result);
      setAttempt(result.attempt);
    } catch (error) {
      toast({
        title: "Error loading exercise",
      });
    }
  };

  useEffect(() => {
    fetchExercise();
  }, []);

  const renderSolution = () => {
    if (!exercise) {
      return null;
    }

    if (exercise.language === "sql") {
      return (
        <CodeEditor
          className="max-h-[400px]"
          language="sql"
          options={{
            lineNumbers: "on",
            readOnly: true,
          }}
          value={exercise.solution}
        />
      );
    }
    return (
      <LatexFormula
        className="mx-3 pb-3 overflow-auto"
        expression={exercise.solution}
      />
    );
  };

  const updateText = async (value: string) => {
    if (!attempt) {
      return;
    }

    const result = await AttemptsService.attemptsPartialUpdate({
      id: attempt.id,
      requestBody: { text: value },
    });
    setAttempt(result);
  };

  const submitAttempt = async () => {
    if (!attempt) {
      return;
    }

    try {
      const { correct } = await AttemptsService.attemptsSubmitCreate({
        id: attempt.id,
      });
    } catch (error) {
      toast({
        title: "Error submitting attempt",
      });
    }
  };

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
              <TabsTrigger value="description">Description</TabsTrigger>
              <TabsTrigger value="editor">Editor</TabsTrigger>
              <TabsTrigger value="solution">Solution</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button onClick={submitAttempt}>Submit</Button>
        </div>
        {tab === "description" && (
          <div className="mx-3">
            <h1 className="mb-4 font-semibold">{exercise.title}</h1>
            <div className="flex gap-2 mb-4">
              <Badge variant="secondary">
                {exercise.language.toUpperCase()}
              </Badge>
              <DifficultyBadge difficulty={exercise.difficulty} />
            </div>
            <div className="text-sm/6">
              <Markdown>{exercise.description}</Markdown>
              <Separator className="mt-3" />
              <Accordion type="multiple">
                <AccordionItem value="database">
                  <AccordionTrigger className="hover:no-underline">
                    <div>
                      <span className="text-muted-foreground font-normal mr-2">
                        Database
                      </span>
                      {exercise.database.name}
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    {exercise.database.description}
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>
        )}
        {tab === "editor" && attempt && (
          <QueryEditor
            query={attempt}
            setQuery={setAttempt}
            updateText={updateText}
          />
        )}
        {tab === "solution" && renderSolution()}
      </QueryPage>
    )
  );
};

export default ExercisePage;
