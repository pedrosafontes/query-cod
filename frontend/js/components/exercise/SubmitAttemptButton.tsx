import { CircleCheckBig } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Attempt, AttemptsService, Feedback } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type SubmitAttemptButtonProps = {
  attempt?: Attempt;
  setFeedback: (feedback?: Feedback) => void;
};

const SubmitAttemptButton = ({
  attempt,
  setFeedback,
}: SubmitAttemptButtonProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [correct, setCorrect] = useState<boolean>();
  const toast = useErrorToast();

  const submitAttempt = async (attempt: Attempt): Promise<void> => {
    setIsSubmitting(true);
    try {
      const feedback = await AttemptsService.attemptsSubmitCreate({
        id: attempt.id,
      });

      setCorrect(feedback.correct);
      setFeedback(feedback);
    } catch (err) {
      toast({
        title: "Error submitting attempt",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const buttonContent = () => {
    if (isSubmitting) {
      return {
        icon: <Spinner className="text-primary-foreground" size="small" />,
      };
    }

    if (correct) {
      return {
        text: "Completed",
        buttonClass: "bg-green-500",
        icon: <CircleCheckBig size={16} />,
      };
    }

    return {};
  };

  const { text, icon, buttonClass } = buttonContent();

  return (
    <Button
      className={buttonClass}
      size="sm"
      variant="default"
      onClick={attempt && (() => submitAttempt(attempt))}
    >
      {icon}
      {text || "Submit"}
    </Button>
  );
};

export default SubmitAttemptButton;
