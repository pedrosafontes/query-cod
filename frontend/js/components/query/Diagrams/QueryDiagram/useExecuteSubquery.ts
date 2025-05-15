import { useState } from "react";

import { QueriesService, QueryResultData } from "api";
import { useErrorToast } from "hooks/useErrorToast";

type ExecuteSubqueryProps = {
  queryId: number;
  subqueryId: number;
  setQueryResult: (result?: QueryResultData) => void;
};

type ExecuteSubqueryReturn = {
  executeSubquery: () => Promise<void>;
  isExecuting: boolean;
};

const useExecuteSubquery = ({
  queryId,
  subqueryId,
  setQueryResult,
}: ExecuteSubqueryProps): ExecuteSubqueryReturn => {
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const toast = useErrorToast();

  const executeSubquery = async () => {
    setIsExecuting(true);
    try {
      const execution = await QueriesService.queriesSubqueriesExecutionsCreate({
        id: queryId,
        subqueryId,
      });

      setQueryResult(execution.results);
    } catch (err) {
      toast({
        title: "Error executing subquery",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return {
    executeSubquery,
    isExecuting,
  };
};

export default useExecuteSubquery;
