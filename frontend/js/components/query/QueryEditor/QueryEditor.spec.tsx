import { render, screen } from "@testing-library/react";

import "@testing-library/jest-dom";
import { Query } from "api";

import RAEditor from "./RAEditor";
import SQLEditor from "./SQLEditor";

import QueryEditor from ".";

jest.mock("./SQLEditor", () => {
  return jest.fn(() => <div data-testid="sql-editor">SQL Editor</div>);
});

jest.mock("./RAEditor", () => {
  return jest.fn(() => <div data-testid="ra-editor">RA Editor</div>);
});

describe("QueryEditor", () => {
  const mockSetQuery = jest.fn();
  const mockUpdateText = jest.fn();

  const mockSQLQuery: Query = {
    id: 1,
    name: "Test Query",
    text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
    assistant_messages: [],
  };

  const mockRAQuery: Query = {
    ...mockSQLQuery,
    language: "ra",
    text: "\\project_{name}Employee",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders SQLEditor when query language is sql", () => {
    render(
      <QueryEditor
        query={mockSQLQuery}
        setQuery={mockSetQuery}
        updateText={mockUpdateText}
      />,
    );

    expect(screen.getByTestId("sql-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("ra-editor")).not.toBeInTheDocument();
    expect(SQLEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockSQLQuery,
        updateText: expect.any(Function),
      }),
      expect.anything(),
    );
  });

  test("renders RAEditor when query language is ra", () => {
    render(
      <QueryEditor
        query={mockRAQuery}
        setQuery={mockSetQuery}
        updateText={mockUpdateText}
      />,
    );

    expect(screen.getByTestId("ra-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("sql-editor")).not.toBeInTheDocument();
    expect(RAEditor).toHaveBeenCalledWith(
      expect.objectContaining({
        query: mockRAQuery,
        updateText: expect.any(Function),
      }),
      expect.anything(),
    );
  });
});
