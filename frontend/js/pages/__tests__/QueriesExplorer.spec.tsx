import {
  render,
  screen,
  waitFor,
  fireEvent,
  act,
} from "@testing-library/react";
import React from "react";

import "@testing-library/jest-dom";
import { QueriesService } from "../../api";
import QueryExplorer from "../../components/QueryExplorer";
import QueryTabs from "../../components/QueryTabs";
import QueriesExplorer from "../QueriesExplorer";

// Mock the dependencies
jest.mock("../../api", () => ({
  QueriesService: {
    queriesList: jest.fn(),
    queriesCreate: jest.fn(),
  },
}));

jest.mock("../../components/QueryExplorer", () => {
  return jest.fn(() => (
    <div data-testid="query-explorer">Query Explorer Component</div>
  ));
});

jest.mock("../../components/QueryTabs", () => {
  return jest.fn().mockImplementation(({ onSelect, onCreate }) => (
    <div data-testid="query-tabs">
      <button data-testid="create-query" type="button" onClick={onCreate}>
        Create Query
      </button>
      <button
        data-testid="select-query"
        type="button"
        onClick={() => onSelect("1")}
      >
        Select Query
      </button>
    </div>
  ));
});

describe("QueriesExplorer Component", () => {
  const mockQueries = [
    { id: 1, text: "Query 1" },
    { id: 2, text: "Query 2" },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (QueriesService.queriesList as jest.Mock).mockResolvedValue(mockQueries);
    (QueriesService.queriesCreate as jest.Mock).mockResolvedValue({
      id: 3,
      text: "",
    });
  });

  test("fetches queries on initial render", async () => {
    await act(async () => {
      render(<QueriesExplorer />);
    });

    expect(QueriesService.queriesList).toHaveBeenCalledTimes(1);
  });

  test("displays QueryTabs with queries data", async () => {
    await act(async () => {
      render(<QueriesExplorer />);
    });

    await waitFor(() => {
      expect(QueryTabs).toHaveBeenCalledWith(
        expect.objectContaining({
          queries: mockQueries,
          currentQueryId: undefined,
        }),
        expect.anything(),
      );
    });
  });

  test("selecting a query updates the currentQueryId state", async () => {
    await act(async () => {
      render(<QueriesExplorer />);
    });

    await waitFor(() => {
      expect(screen.getByTestId("query-tabs")).toBeInTheDocument();
    });

    // Click on the select query button which will call onSelect with '1'
    fireEvent.click(screen.getByTestId("select-query"));

    await waitFor(() => {
      expect(QueryTabs).toHaveBeenLastCalledWith(
        expect.objectContaining({
          currentQueryId: "1",
        }),
        expect.anything(),
      );
    });

    // The QueryExplorer should now be rendered with the selected query
    await waitFor(() => {
      expect(QueryExplorer).toHaveBeenCalledWith(
        expect.objectContaining({
          query: expect.objectContaining({ id: 1 }),
        }),
        expect.anything(),
      );
    });
  });

  test("creating a new query calls queriesCreate and refreshes the list", async () => {
    await act(async () => {
      render(<QueriesExplorer />);
    });

    await waitFor(() => {
      expect(screen.getByTestId("query-tabs")).toBeInTheDocument();
    });

    // Click on the create query button
    fireEvent.click(screen.getByTestId("create-query"));

    expect(QueriesService.queriesCreate).toHaveBeenCalledWith({
      requestBody: {
        text: "",
      },
    });

    // Wait for the second call to queriesList (after creation)
    await waitFor(() => {
      expect(QueriesService.queriesList).toHaveBeenCalledTimes(2);
    });
  });
});
