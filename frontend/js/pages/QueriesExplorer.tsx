import { useEffect, useState } from "react";

import { QueriesService, Query } from "../api";
import QueryExplorer from "../components/QueryExplorer";
import QueryTabs from "../components/QueryTabs";

const QueriesExplorer = () => {
  const [queries, setQueries] =
    useState<Awaited<ReturnType<typeof QueriesService.queriesList>>>();
  const [currentQueryId, setCurrentQueryId] = useState<string | undefined>(undefined);

  const query = queries?.find(
    (query) => query.id.toString() === currentQueryId
  );

  const fetchQueries = async () => {
    const result = await QueriesService.queriesList();
    setQueries(result);
  };

  const createQuery = async (): Promise<void> => {
    try {
      await QueriesService.queriesCreate({
        requestBody: {
          text: "",
        } as Query,
      });

      fetchQueries();
    } catch (error) {
      console.error("Error creating query:", error);
    }
  };

  useEffect(() => {
    fetchQueries();
  }, []);

  return (
    <div className="w-screen h-screen">
      <div className="grid grid-cols-8 gap-4 h-full">
        <div className="col-span-1 overflow-auto px-3 border-r py-5">
          {queries && (
            <QueryTabs
              queries={queries}
              currentQueryId={currentQueryId}
              onSelect={setCurrentQueryId}
              onCreate={createQuery}
            />
          )}
        </div>
        <div className="col-span-7">
          {query && <QueryExplorer query={query} key={query.id} />}
        </div>
      </div>
    </div>
  );
};

export default QueriesExplorer;
