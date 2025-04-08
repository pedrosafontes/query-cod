import { EditorProps } from "@monaco-editor/react";
import { render, screen } from "@testing-library/react";
import type { editor } from "monaco-editor";

import { Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import QueryEditor from "../QueryEditor";

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

jest.mock("js/hooks/useAutosave", () => ({
  useAutosave: jest.fn(),
}));

jest.mock("js/api", () => ({
  QueriesService: {
    queriesPartialUpdate: jest.fn(),
  },
}));

describe("QueryEditor", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    text: "SELECT * FROM users;",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the editor with initial text", async () => {
    (useAutosave as jest.Mock).mockReturnValue("saved");

    render(<QueryEditor query={mockQuery} />);

    const editor = screen.getByTestId("monaco-editor");
    expect(editor).toHaveValue(mockQuery.text);
  });

  test("shows loading state during save", async () => {
    (useAutosave as jest.Mock).mockReturnValue("saving");

    render(<QueryEditor query={mockQuery} />);

    expect(screen.getByText(/saving/i)).toBeInTheDocument();
  });

  test("shows error state when save fails", async () => {
    (useAutosave as jest.Mock).mockReturnValue("error");

    render(<QueryEditor query={mockQuery} />);

    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  test("shows saved state after successful save", async () => {
    (useAutosave as jest.Mock).mockReturnValue("saved");

    render(<QueryEditor query={mockQuery} />);

    expect(screen.getByText(/saved/i)).toBeInTheDocument();
  });
});
