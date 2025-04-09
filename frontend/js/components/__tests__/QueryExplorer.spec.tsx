import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";

import "@testing-library/jest-dom";
import { QueriesService, Query } from "api";

import QueryEditor from "../QueryEditor";
import QueryExplorer from "../QueryExplorer";
import QueryResult from "../QueryResult";

jest.mock("api");
const mockToast = jest.fn();
jest.mock("hooks/use-toast", () => ({
  useToast: () => ({ toast: mockToast }),
}));

jest.mock("../QueryEditor", () => {
  return jest.fn(() => (
    <div data-testid="query-editor">Query Editor Component</div>
  ));
});

jest.mock("../QueryResult", () => {
  return jest.fn(() => (
    <div data-testid="query-result">Query Result Component</div>
  ));
});

describe("QueryExplorer Component", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    text: "SELECT * FROM users",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
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

  beforeEach(() => {
    jest.clearAllMocks();
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockResolvedValue(
      mockExecutionResult,
    );
  });

  test("renders the component with QueryEditor", async () => {
    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    expect(screen.getByText("Execute")).toBeInTheDocument();
    expect(screen.getByTestId("query-editor")).toBeInTheDocument();

    expect(QueryEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockQuery,
      }),
      expect.anything(),
    );
  });

  test("executes query when Execute button is clicked", async () => {
    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    fireEvent.click(screen.getByText("Execute"));

    expect(QueriesService.queriesExecutionsCreate).toHaveBeenCalledWith({
      id: mockQuery.id,
    });

    await waitFor(() => {
      expect(QueryResult).toHaveBeenCalledWith(
        expect.objectContaining({
          result: mockExecutionResult.results,
          isLoading: false,
        }),
        expect.anything(),
      );
    });
  });

  test("disables execute button while loading", async () => {
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(() => resolve(mockExecutionResult), 100),
        ),
    );

    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    const executeButton = screen.getByRole("button", { name: /execute/i });
    fireEvent.click(executeButton);

    expect(executeButton).toBeDisabled();
    await waitFor(() => expect(executeButton).not.toBeDisabled());
  });

  test("handles execution error and shows toast", async () => {
    (QueriesService.queriesExecutionsCreate as jest.Mock).mockRejectedValue(
      new Error("Execution failed"),
    );

    await act(async () => {
      render(<QueryExplorer query={mockQuery} />);
    });

    fireEvent.click(screen.getByText("Execute"));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Error executing query" }),
      );
    });
  });
});
