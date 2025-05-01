import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { userEvent } from "@testing-library/user-event";

import { LanguageEnum, QueriesService, Query } from "api";
import * as useErrorToastModule from "hooks/useErrorToast";

import QueryLanguageTabs from "./QueryLanguageTabs";

jest.mock("api", () => ({
  QueriesService: {
    queriesPartialUpdate: jest.fn(),
  },
}));

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: jest.fn(),
}));

describe("QueryLanguageTabs", () => {
  const mockQuery: Query = {
    id: 1,
    name: "Test Query",
    sql_text: "SELECT * FROM users",
    language: "sql",
    created: new Date().toISOString(),
    modified: new Date().toISOString(),
    validation_errors: [],
  };

  const mockSetQuery = jest.fn();
  const mockSetIsLoading = jest.fn();
  const mockToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useErrorToastModule.useErrorToast as jest.Mock).mockReturnValue(mockToast);
  });

  test("renders the language tabs with the current language selected", () => {
    render(
      <QueryLanguageTabs
        query={mockQuery}
        setIsLoading={mockSetIsLoading}
        setQuery={mockSetQuery}
      />,
    );

    const sqlTab = screen.getByRole("tab", { name: /sql/i });
    const raTab = screen.getByRole("tab", { name: /relational algebra/i });

    expect(
      mockQuery.language === ("sql" as LanguageEnum) ? sqlTab : raTab,
    ).toHaveAttribute("data-state", "active");
    expect(
      mockQuery.language === ("sql" as LanguageEnum) ? raTab : sqlTab,
    ).toHaveAttribute("data-state", "inactive");
  });

  test("switches language when a different tab is clicked", async () => {
    const updatedQuery = { ...mockQuery, language: "ra" };
    (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue(
      updatedQuery,
    );

    render(
      <QueryLanguageTabs
        query={mockQuery}
        setIsLoading={mockSetIsLoading}
        setQuery={mockSetQuery}
      />,
    );

    const raTab = screen.getByRole("tab", { name: /relational algebra/i });
    const user = userEvent.setup();
    await user.click(raTab);

    expect(mockSetIsLoading).toHaveBeenCalledWith(true);
    expect(QueriesService.queriesPartialUpdate).toHaveBeenCalledWith({
      id: mockQuery.id,
      requestBody: {
        language: "ra",
      },
    });

    await waitFor(() => {
      expect(mockSetQuery).toHaveBeenCalledWith(updatedQuery);
      expect(mockSetIsLoading).toHaveBeenCalledWith(false);
    });
  });

  test("shows an error toast and reverts language when API call fails", async () => {
    (QueriesService.queriesPartialUpdate as jest.Mock).mockRejectedValue(
      new Error("API Error"),
    );

    render(
      <QueryLanguageTabs
        query={mockQuery}
        setIsLoading={mockSetIsLoading}
        setQuery={mockSetQuery}
      />,
    );

    const raTab = screen.getByRole("tab", { name: /relational algebra/i });
    const user = userEvent.setup();
    await user.click(raTab);

    expect(mockSetIsLoading).toHaveBeenCalledWith(true);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error updating query language",
      });
      expect(mockSetIsLoading).toHaveBeenCalledWith(false);
    });
  });

  test("doesn't call API when clicking on the already selected language", async () => {
    render(
      <QueryLanguageTabs
        query={mockQuery}
        setIsLoading={mockSetIsLoading}
        setQuery={mockSetQuery}
      />,
    );

    const sqlTab = screen.getByRole("tab", { name: /sql/i });
    const user = userEvent.setup();
    await user.click(sqlTab);

    expect(QueriesService.queriesPartialUpdate).not.toHaveBeenCalled();
  });
});
