import { CircleCheckBigIcon, CircleX } from "lucide-react";

import { Feedback, QueryResultData } from "api";

import QueryResult from "../query/QueryResult";

type FeedbackProps = {
  feedback: Feedback;
  solutionData: QueryResultData;
};

const ExerciseFeedback = ({ feedback, solutionData }: FeedbackProps) => {
  return (
    <div className="mx-3 mt-5">
      {feedback.correct ? (
        <>
          <h3 className="font-semibold mb-3 flex gap-2 items-center">
            <CircleCheckBigIcon className="size-4 text-green-500" /> Your query
            returned the correct result!
          </h3>
          <p className="text-muted-foreground text-sm">
            You can now compare your solution with the sample solution to see if
            there is a different or more efficient approach.
          </p>
        </>
      ) : (
        <>
          <h3 className="font-semibold mb-3 flex gap-2 items-center">
            <CircleX className="size-4 text-red-500" /> Your query did not
            return the correct result.
          </h3>
          <p className="text-muted-foreground text-sm mb-4">
            Try reviewing your logic or the structure of your query. You can
            compare your result with the expected output below.
          </p>
          <QueryResult pageSize={10} result={solutionData} />
        </>
      )}
    </div>
  );
};

export default ExerciseFeedback;
