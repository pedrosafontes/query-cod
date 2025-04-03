import { useEffect, useState } from "react";

import { QueriesService, Query } from "../api";
import QueryExplorer from "../components/QueryExplorer";
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

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
          <div className="sticky top-0 z-10 mb-3 bg-white">
            <Button variant="outline" onClick={createQuery} size="sm" className="w-full">
              New Query
            </Button>
          </div>
          <div className="overflow-y-auto flex-1 pr-1">
            <Tabs value={currentQueryId} onValueChange={setCurrentQueryId}>
              <TabsList className="flex flex-col h-auto w-full">
                {queries && queries.map((query) => (
                  <TabsTrigger key={query.id} value={query.id.toString()}>
                    Query {query.id}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        </div>
        <div className="col-span-7">
          {query && <QueryExplorer query={query} key={query.id} />}
        </div>
      </div>
    </div>
  );
};

export default QueriesExplorer;
