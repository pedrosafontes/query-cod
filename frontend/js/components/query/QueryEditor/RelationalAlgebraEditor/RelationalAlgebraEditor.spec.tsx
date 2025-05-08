import { render, screen } from "@testing-library/react";

import "@testing-library/jest-dom";
import { QueriesService, Query } from "api";
import { useAutosave } from "hooks/useAutosave";

import RelationalAlgebraEditor from ".";

jest.mock("react-markdown");
jest.mock("rehype-raw");

jest.mock("mathlive");

jest.mock("hooks/useAutosave", () => ({
  useAutosave: jest.fn(),
}));

jest.mock("api", () => ({
  QueriesService: {
    queriesPartialUpdate: jest.fn(),
  },
}));

describe("RelationalAlgebraEditor", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    ra_text: "\\pi_{name}(Person)",
    language: "ra",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
  };

  const mockSetQuery = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAutosave as jest.Mock).mockReturnValue("saved");
    (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue(
      mockQuery,
    );
  });

  test("renders with initial RA text", () => {
    const { container } = render(
      <RelationalAlgebraEditor query={mockQuery} setQuery={mockSetQuery} />,
    );

    const mathField = container.querySelector("math-field");
    expect(mathField).toBeInTheDocument();
    expect(mathField).toHaveTextContent(mockQuery.ra_text as string);
  });

  test("calls useAutosave with correct initial data", () => {
    render(
      <RelationalAlgebraEditor query={mockQuery} setQuery={mockSetQuery} />,
    );

    expect(useAutosave).toHaveBeenCalledWith({
      data: mockQuery.ra_text,
      onSave: expect.any(Function),
    });
  });

  test("displays autosave status", () => {
    (useAutosave as jest.Mock).mockReturnValue("saving");

    render(
      <RelationalAlgebraEditor query={mockQuery} setQuery={mockSetQuery} />,
    );

    expect(screen.getByText(/saving/i)).toBeInTheDocument();
  });

  test("displays ErrorAlert when there are errors", () => {
    const mockErrorQuery = {
      ...mockQuery,
      validation_errors: [{ title: "Error 1" }, { title: "Error 2" }],
    };

    render(
      <RelationalAlgebraEditor
        query={mockErrorQuery}
        setQuery={mockSetQuery}
      />,
    );

    expect(screen.getByText("Error 1")).toBeInTheDocument();
    expect(screen.getByText("Error 2")).toBeInTheDocument();
  });
});
