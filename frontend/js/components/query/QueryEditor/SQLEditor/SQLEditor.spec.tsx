import { EditorProps } from "@monaco-editor/react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { editor } from "monaco-editor";

import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import SQLEditor from ".";

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
    text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
    assistant_messages: [],
  };

  const mockUpdateText = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAutosave as jest.Mock).mockReturnValue("saved");
    (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue(
      mockQuery,
    );
  });

  test("renders the editor with initial SQL text", () => {
    render(<SQLEditor query={mockQuery} updateText={mockUpdateText} />);

    const editor = screen.getByTestId("monaco-editor");
    expect(editor).toBeInTheDocument();
    expect(editor).toHaveValue("SELECT * FROM users");
  });

  test("calls useAutosave with correct parameters", () => {
    render(<SQLEditor query={mockQuery} updateText={mockUpdateText} />);

    expect(useAutosave).toHaveBeenCalledWith({
      data: mockQuery.text,
      onSave: expect.any(Function),
    });
  });

  test("displays autosave status", () => {
    (useAutosave as jest.Mock).mockReturnValue("saving");

    render(<SQLEditor query={mockQuery} updateText={mockUpdateText} />);

    expect(screen.getByText(/saving/i)).toBeInTheDocument();
  });

  test("handles queries with no SQL text", () => {
    const emptyQuery = {
      ...mockQuery,
      text: undefined,
    };

    render(<SQLEditor query={emptyQuery} updateText={mockUpdateText} />);

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

    render(<SQLEditor query={mockErrorQuery} updateText={mockUpdateText} />);

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

    render(<SQLEditor query={mockErrorQuery} updateText={mockUpdateText} />);

    expect(screen.queryByText("Error with position")).not.toBeInTheDocument();
  });
});
