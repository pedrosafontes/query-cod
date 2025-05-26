import { render, screen, waitFor } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";

import { ProjectsService } from "api";

import CreateQueryButton from "./CreateQueryButton";

jest.mock("api");

const mockToast = jest.fn();
jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: () => mockToast,
}));

describe("CreateQueryButton", () => {
  const projectId = 1;
  const onSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("creates a new SQL query", async () => {
    (ProjectsService.projectsQueriesCreate as jest.Mock).mockResolvedValue({
      id: 999,
      name: "Untitled",
      text: "",
    });

    render(
      <CreateQueryButton projectId={projectId} onSuccess={onSuccess}>
        <button type="button">Create Query</button>
      </CreateQueryButton>,
    );

    await userEvent.click(
      screen.getByRole("button", { name: /create query/i }),
    );

    const sqlItem = await screen.findByRole("menuitem", { name: "SQL" });
    await userEvent.click(sqlItem);

    await waitFor(() =>
      expect(ProjectsService.projectsQueriesCreate).toHaveBeenCalledWith({
        projectPk: projectId,
        requestBody: {
          name: "Untitled",
          language: "sql",
        },
      }),
    );

    expect(onSuccess).toHaveBeenCalledWith(999);
  });

  test("creates a new RA query", async () => {
    (ProjectsService.projectsQueriesCreate as jest.Mock).mockResolvedValue({
      id: 1000,
      name: "Untitled",
      text: "",
    });

    render(
      <CreateQueryButton projectId={projectId} onSuccess={onSuccess}>
        <button type="button">Create Query</button>
      </CreateQueryButton>,
    );

    await userEvent.click(
      screen.getByRole("button", { name: /create query/i }),
    );

    const raItem = await screen.findByRole("menuitem", { name: "RA" });
    await userEvent.click(raItem);

    expect(ProjectsService.projectsQueriesCreate).toHaveBeenCalledWith({
      projectPk: projectId,
      requestBody: {
        name: "Untitled",
        language: "ra",
      },
    });

    expect(onSuccess).toHaveBeenCalledWith(1000);
  });

  test("handles network error during query creation", async () => {
    (ProjectsService.projectsQueriesCreate as jest.Mock).mockRejectedValue(
      new Error("Create error"),
    );

    render(
      <CreateQueryButton projectId={projectId}>
        <button type="button">Create Query</button>
      </CreateQueryButton>,
    );

    await userEvent.click(
      screen.getByRole("button", { name: /create query/i }),
    );

    const sqlItem = await screen.findByRole("menuitem", { name: "SQL" });
    await userEvent.click(sqlItem);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: expect.stringMatching(/error/i) }),
      );
    });
  });
});
