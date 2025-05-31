import { CircleCheckBigIcon } from "lucide-react";
import Markdown from "marked-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Exercise } from "api";

import DifficultyBadge from "./DifficultyBadge";

const ExerciseDetails = ({
  exercise,
  className,
}: {
  exercise: Exercise;
  className: string;
}) => {
  return (
    <div className={className}>
      <h1 className="mb-4 font-semibold flex gap-4 items-center">
        {exercise.title}
        {exercise.completed && (
          <span className="flex gap-1 font-normal text-muted-foreground text-xs items-center">
            <CircleCheckBigIcon className="size-3 text-green-500" /> Completed
          </span>
        )}
      </h1>
      <div className="flex gap-2 mb-4">
        <Badge variant="secondary">{exercise.language.toUpperCase()}</Badge>
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
            <AccordionContent className="text-sm/6">
              <Markdown>
                {exercise.database.description}
              </Markdown>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
};

export default ExerciseDetails;
