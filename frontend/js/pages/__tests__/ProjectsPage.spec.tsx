import { render, screen, waitFor, fireEvent } from "@testing-library/react";

import { ProjectsService } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import ProjectsPage from "../ProjectsPage";

jest.mock("api", () => ({
  ProjectsService: {
    projectsList: jest.fn(),
  },
}));

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: jest.fn(),
}));

jest.mock("components/ProjectForm", () => () => <div>Mock ProjectForm</div>);
jest.mock("components/ProjectActions", () => () => (
  <div>Mock ProjectActions</div>
));

describe("ProjectsPage", () => {
  const mockToast = jest.fn();
  const mockProjects = [
    {
      id: 1,
      name: "Project One",
      database: {
        id: 0,
        name: "Database One",
      },
      last_modified: new Date().toISOString(),
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      queries: [],
    },
    {
      id: 2,
      name: "Project Two",
      database: {
        id: 1,
        name: "Database Two",
      },
      last_modified: new Date().toISOString(),
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      queries: [],
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (useErrorToast as jest.Mock).mockReturnValue(mockToast);
    (ProjectsService.projectsList as jest.Mock).mockResolvedValue(mockProjects);
  });

  test("fetches and renders projects", async () => {
    render(<ProjectsPage />);

    expect(ProjectsService.projectsList).toHaveBeenCalledTimes(1);

    await waitFor(() => {
      expect(screen.getByRole("table")).toHaveTextContent("Project One");
      expect(screen.getByRole("table")).toHaveTextContent("Project Two");
    });
  });

  test("opens the dialog when 'New Project' button is clicked", async () => {
    render(<ProjectsPage />);

    const newProjectButton = screen.getByRole("button", {
      name: /new project/i,
    });
    fireEvent.click(newProjectButton);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /new project/i }),
      ).toBeInTheDocument();
      expect(screen.getByText("Mock ProjectForm")).toBeInTheDocument();
    });
  });

  test("shows an error toast when API call fails", async () => {
    (ProjectsService.projectsList as jest.Mock).mockRejectedValueOnce(
      new Error("API failure"),
    );
    render(<ProjectsPage />);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error loading projects",
      });
    });
  });
});
