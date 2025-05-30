import { CircleCheckBig, CircleX } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Attempt, AttemptsService } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type SubmitAttemptButtonProps = {
  attempt?: Attempt;
};

const SubmitAttemptButton = ({ attempt }: SubmitAttemptButtonProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [correct, setCorrect] = useState<boolean>();
  const toast = useErrorToast();

  const submitAttempt = async (attempt: Attempt): Promise<void> => {
    setIsSubmitting(true);
    try {
      const { correct } = await AttemptsService.attemptsSubmitCreate({
        id: attempt.id,
      });
      setCorrect(correct);
    } catch (err) {
      toast({
        title: "Error submitting attempt",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const buttonContent = () => {
    const isCorrect = Boolean(correct);

    if (isSubmitting) {
      return {
        icon: <Spinner className="text-primary-foreground" size="small" />,
      };
    }
    if (correct === undefined) {
      return {};
    }
    if (isCorrect) {
      return {
        text: "Well done!",
        buttonClass: "bg-green-500",
        icon: <CircleCheckBig size={16} />,
      };
    }
    if (!isCorrect) {
      return {
        text: "Try Again",
        buttonClass: "bg-red-500",
        icon: <CircleX size={16} />,
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
