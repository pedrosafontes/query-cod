import { render, screen, waitFor } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";

import { LanguageEnum, QueriesService } from "api";

import { SidebarProvider } from "../ui/sidebar";

import QueryMenuItem from "./QueryMenuItem";

jest.mock("api");
const mockToast = jest.fn();
jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
}));

describe("QueryMenuItem", () => {
  const baseProps = {
    query: { id: 1, name: "Test Query", language: "ra" as LanguageEnum },
    isActive: false,
    onSelect: jest.fn(),
    onRename: jest.fn(),
    onDelete: jest.fn(),
  };

  const renderQueryMenuItem = () => {
    return render(
      <SidebarProvider>
        <QueryMenuItem {...baseProps} />
      </SidebarProvider>,
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders query name", () => {
    renderQueryMenuItem();
    expect(screen.getByText("Test Query")).toBeInTheDocument();
  });

  test("enters rename mode on double click and renames query", async () => {
    (QueriesService.queriesPartialUpdate as jest.Mock).mockResolvedValue({});
    renderQueryMenuItem();

    await userEvent.dblClick(screen.getByText("Test Query"));
    const input = await screen.findByDisplayValue("Test Query");
    await userEvent.clear(input);
    await userEvent.type(input, "Renamed Query");
    await userEvent.keyboard("{Enter}");

    expect(QueriesService.queriesPartialUpdate).toHaveBeenCalledWith({
      id: 1,
      requestBody: { name: "Renamed Query" },
    });
    expect(baseProps.onRename).toHaveBeenCalled();
  });

  test("shows error toast if rename fails", async () => {
    (QueriesService.queriesPartialUpdate as jest.Mock).mockRejectedValueOnce(
      new Error("Rename failed"),
    );

    renderQueryMenuItem();

    await userEvent.dblClick(screen.getByText("Test Query"));
    const input = await screen.findByDisplayValue("Test Query");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    await userEvent.keyboard("{Enter}");

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Error renaming query" }),
      );
    });
  });

  test("opens dropdown and deletes query", async () => {
    (QueriesService.queriesDestroy as jest.Mock).mockResolvedValue({});

    renderQueryMenuItem();

    const actionsButton = screen.getByRole("button", { name: /actions/i });
    await userEvent.click(actionsButton);

    const deleteItem = await screen.findByRole("menuitem", {
      name: /delete query/i,
    });
    await userEvent.click(deleteItem);

    expect(QueriesService.queriesDestroy).toHaveBeenCalledWith({ id: 1 });
    expect(baseProps.onDelete).toHaveBeenCalledWith(1);
  });

  test("shows error toast if delete fails", async () => {
    (QueriesService.queriesDestroy as jest.Mock).mockRejectedValueOnce(
      new Error("Delete failed"),
    );

    renderQueryMenuItem();

    const actionsButton = screen.getByRole("button", { name: /actions/i });
    await userEvent.click(actionsButton);

    const deleteItem = await screen.findByRole("menuitem", {
      name: /delete query/i,
    });
    await userEvent.click(deleteItem);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Error deleting query" }),
      );
    });
  });
});
