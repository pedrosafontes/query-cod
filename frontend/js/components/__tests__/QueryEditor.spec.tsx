import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import QueryEditor from "../QueryEditor";
import { QueriesService } from "js/api";
import { useAutosave } from "js/hooks/useAutosave";
import { useEffect } from "react";

// Mock MonacoEditor
jest.mock("@monaco-editor/react", () => ({
  __esModule: true,
  default: ({ onChange, value }: any) => {
    return (
      <textarea
        data-testid="monaco-editor"
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
  const fakeQuery = {
    id: 1,
    text: "SELECT * FROM users;",
    created: "2024-01-01T00:00:00Z",
    modified: "2024-01-02T00:00:00Z",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the editor with initial text", async () => {
    (useAutosave as jest.Mock).mockReturnValue("saved");

    render(<QueryEditor query={fakeQuery} />);

    const editor = screen.getByTestId("monaco-editor");
    expect(editor).toBeInTheDocument();
    expect(editor).toHaveValue(fakeQuery.text);
    expect(screen.getByText("Saved!")).toBeInTheDocument();
  });

  it("calls autosave on change", async () => {
    (useAutosave as jest.Mock).mockImplementation(({ onSave }) => {
      onSave("SELECT 1");
      return "saving";
    });

    render(<QueryEditor query={fakeQuery} />);
    const editor = screen.getByTestId("monaco-editor");

    fireEvent.change(editor, { target: { value: "SELECT 1" } });

    await waitFor(() => {
      expect(QueriesService.queriesPartialUpdate).toHaveBeenCalledWith({
        id: 1,
        requestBody: { text: "SELECT 1" },
      });
    });

    expect(screen.getByText(/Saving/i)).toBeInTheDocument();
  });

  it("displays error status on autosave failure", async () => {
    (useAutosave as jest.Mock).mockReturnValue("error");

    render(<QueryEditor query={fakeQuery} />);
    expect(screen.getByText(/Error saving/i)).toBeInTheDocument();
  });
});
