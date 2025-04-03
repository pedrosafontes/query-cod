import { useEffect, useState } from "react";
import { Button, Tab, Tabs } from "react-bootstrap";

import { QueriesService, Query } from "../api";
import QueryExplorer from "../components/QueryExplorer";

const QueriesExplorer = () => {
  const [queries, setQueries] =
    useState<Awaited<ReturnType<typeof QueriesService.queriesList>>>();

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
    <div className="container">
      <div className="d-flex justify-content-between align-items-center my-2">
        <Button size="sm" variant="primary" onClick={createQuery}>
          New Query
        </Button>
      </div>
      <Tabs className="mb-3" id="queries">
        {queries &&
          queries.results.map((query: Query) => (
            <Tab key={query.id} eventKey={query.id} title={query.id}>
              <QueryExplorer query={query} />
            </Tab>
          ))}
      </Tabs>
    </div>
  );
};

export default QueriesExplorer;
