import { EditorProps } from "@monaco-editor/react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { editor } from "monaco-editor";

import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import SQLEditor from ".";

jest.mock("react-markdown");
jest.mock("rehype-raw");

// Mock MonacoEditor
jest.mock("@monaco-editor/react", () => ({
  __esModule: true,
  default: ({ onChange, value }: EditorProps) => {
    return (
      <textarea
        data-testid="monaco-editor"
        value={value}
        onChange={(e) =>
          onChange?.(
            e.target.value ?? "",
            {} as editor.IModelContentChangedEvent,
          )
        }
      />
    );
  },
}));

jest.mock("hooks/useAutosave", () => ({
  useAutosave: jest.fn(),
}));

jest.mock("api", () => ({
  QueriesService: {
    queriesPartialUpdate: jest.fn(),
  },
}));

describe("SQLEditor", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    sql_text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
  };

  const mockOnErrorsChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAutosave as jest.Mock).mockReturnValue("saved");
    (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue(
      mockQuery,
    );
  });

  test("renders the editor with initial SQL text", () => {
    render(<SQLEditor query={mockQuery} onErrorsChange={mockOnErrorsChange} />);

    const editor = screen.getByTestId("monaco-editor");
    expect(editor).toBeInTheDocument();
    expect(editor).toHaveValue("SELECT * FROM users");
  });

  test("calls useAutosave with correct parameters", () => {
    render(<SQLEditor query={mockQuery} onErrorsChange={mockOnErrorsChange} />);

    expect(useAutosave).toHaveBeenCalledWith({
      data: mockQuery.sql_text,
      onSave: expect.any(Function),
    });
  });

  test("displays autosave status", () => {
    (useAutosave as jest.Mock).mockReturnValue("saving");

    render(<SQLEditor query={mockQuery} onErrorsChange={mockOnErrorsChange} />);

    expect(screen.getByText(/saving/i)).toBeInTheDocument();
  });

  test("sets up error markers when editor mounts", async () => {
    const queryWithErrors = {
      ...mockQuery,
      validation_errors: [
        {
          title: "Syntax error",
          position: {
            line: 1,
            start_col: 1,
            end_col: 5,
          },
        },
      ],
    };

    render(
      <SQLEditor query={queryWithErrors} onErrorsChange={mockOnErrorsChange} />,
    );

    await waitFor(() => {
      expect(mockOnErrorsChange).toHaveBeenCalledWith(
        queryWithErrors.validation_errors,
      );
    });
  });

  test("handles queries with no SQL text", () => {
    const emptyQuery = {
      ...mockQuery,
      sql_text: undefined,
    };

    render(
      <SQLEditor query={emptyQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    const editor = screen.getByTestId("monaco-editor");
    expect(editor).toHaveValue("");
  });

  test("displays ErrorAlert when there are general errors", () => {
    const mockErrorQuery = {
      ...mockQuery,
      validation_errors: [
        { title: "General error 1" },
        { title: "General error 2" },
      ],
    };

    render(
      <SQLEditor query={mockErrorQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(screen.getByText("General error 1")).toBeInTheDocument();
    expect(screen.getByText("General error 2")).toBeInTheDocument();
  });

  test("doesn't display ErrorAlert when there are no general errors", () => {
    const mockErrorQuery = {
      ...mockQuery,
      validation_errors: [
        {
          title: "Error with position",
          position: { line: 1, start_col: 5, end_col: 10 },
        },
      ],
    };

    render(
      <SQLEditor query={mockErrorQuery} onErrorsChange={mockOnErrorsChange} />,
    );

    expect(screen.queryByText("Error with position")).not.toBeInTheDocument();
  });
});
