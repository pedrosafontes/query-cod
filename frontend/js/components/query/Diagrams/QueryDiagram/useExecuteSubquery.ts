import { useContext, useState } from "react";

import { QueryResultData } from "api";
import { QueryContext } from "contexts/QueryContext";
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

  const { executeSubquery: executeSubqueryService } = useContext(QueryContext)!;

  const executeSubquery = async () => {
    setIsExecuting(true);
    try {
      const execution = await executeSubqueryService({
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
