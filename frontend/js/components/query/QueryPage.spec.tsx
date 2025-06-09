import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";

import "@testing-library/jest-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueriesService, Query } from "api";

import ProjectQuery from "../project/ProjectQuery";

import { DiagramsProps } from "./Diagrams";
import QueryEditor from "./QueryEditor";
import QueryResult from "./QueryResult";

jest.mock("api");
const mockToast = jest.fn();
jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
}));

jest.mock("./QueryEditor", () => {
  return jest.fn(() => (
    <div data-testid="query-editor">Query Editor Component</div>
  ));
});

jest.mock("./QueryResult", () => {
  return jest.fn(() => (
    <div data-testid="query-result">Query Result Component</div>
  ));
});

jest.mock("./Diagrams", () => {
  return jest.fn(({ children }: DiagramsProps) => (
    <div data-testid="query-diagrams">{children}</div>
  ));
});

describe("ProjectQuery", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
    assistant_messages: [],
  };

  const mockExecutionResult = {
    success: true,
    results: {
      columns: ["id", "name", "email"],
      rows: [
        [1, "John Doe", "john@example.com"],
        [2, "Jane Smith", "jane@example.com"],
      ],
    },
  };

  const mockSetQueryId = jest.fn();

  const renderComponent = () =>
    render(
      <TooltipProvider>
        <ProjectQuery
          databaseId={0}
          queryId={mockQuery.id}
          refetchProject={jest.fn()}
          setQueryId={mockSetQueryId}
        />
      </TooltipProvider>,
    );

  beforeEach(() => {
    jest.clearAllMocks();
    (QueriesService.queriesRetrieve as jest.Mock).mockResolvedValue(mockQuery);
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockResolvedValue(
      mockExecutionResult,
    );
  });

  test("fetches the query and renders the QueryEditor", async () => {
    await act(async () => {
      renderComponent();
    });

    expect(QueriesService.queriesRetrieve).toHaveBeenCalledWith({
      id: mockQuery.id,
    });

    expect(screen.getByText("Execute")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId("query-editor")).toBeInTheDocument();

      expect(QueryEditor).toHaveBeenCalledWith(
        expect.objectContaining({
          query: mockQuery,
        }),
        expect.anything(),
      );
    });
  });

  test("executes query when Execute button is clicked", async () => {
    await act(async () => {
      renderComponent();
    });

    fireEvent.click(screen.getByText("Execute"));

    expect(QueriesService.queriesExecutionsCreate).toHaveBeenCalledWith({
      id: mockQuery.id,
    });

    await waitFor(() => {
      expect(QueryResult).toHaveBeenCalledWith(
        expect.objectContaining({
          result: mockExecutionResult.results,
        }),
        expect.anything(),
      );
    });
  });

  test("handles execution error and shows toast", async () => {
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockRejectedValue(
      new Error("Execution failed"),
    );

    await act(async () => {
      renderComponent();
    });

    fireEvent.click(screen.getByText("Execute"));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Error executing query" }),
      );
    });
  });
});
