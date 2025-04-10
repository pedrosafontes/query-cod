import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useNavigate } from "react-router";

import { Project, ProjectsService } from "api";
import { useErrorToast } from "hooks/useErrorToast";

import ProjectActions from "../ProjectActions";
import { ProjectFormProps } from "../ProjectForm";

jest.mock("api", () => ({
  ProjectsService: {
    projectsDestroy: jest.fn(),
  },
}));

jest.mock("hooks/useErrorToast", () => ({
  useErrorToast: jest.fn(),
}));

jest.mock("react-router", () => ({
  useNavigate: jest.fn(),
}));

jest.mock(
  "components/ProjectForm",
  () =>
    ({ project, onSuccess }: ProjectFormProps) => (
      <div>
        <div>Edit Form for {project?.name}</div>
        <button type="submit" onClick={() => onSuccess?.()}>
          Submit
        </button>
      </div>
    ),
);

describe("ProjectActions", () => {
  const mockDelete = ProjectsService.projectsDestroy as jest.Mock;
  const mockToast = jest.fn();
  const mockNavigate = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useErrorToast as jest.Mock).mockReturnValue(mockToast);
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  const project = {
    id: 1,
    name: "Test Project",
    database: { name: "testdb" },
    created: new Date().toISOString(),
    last_modified: new Date().toISOString(),
  } as Project;

  test("calls deleteProject and onSuccess when delete succeeds", async () => {
    mockDelete.mockResolvedValue({});

    render(<ProjectActions project={project} onSuccess={mockOnSuccess} />);
    fireEvent.click(screen.getByRole("button", { name: /delete project/i }));

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith({ id: project.id });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  test("shows toast on delete failure", async () => {
    mockDelete.mockRejectedValue(new Error("Delete failed"));

    render(<ProjectActions project={project} onSuccess={mockOnSuccess} />);
    fireEvent.click(screen.getByRole("button", { name: /delete project/i }));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Error deleting project",
      });
    });
  });

  test("opens and submits the edit dialog", async () => {
    render(<ProjectActions project={project} onSuccess={mockOnSuccess} />);
    fireEvent.click(screen.getByRole("button", { name: /edit project/i }));

    expect(screen.getByText(/Edit Form for Test Project/)).toBeInTheDocument();

    fireEvent.click(screen.getByText("Submit"));

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });

    expect(screen.queryByText(/Edit Form for/)).not.toBeInTheDocument();
  });

  test("navigates to project page on Open click", () => {
    render(<ProjectActions project={project} onSuccess={mockOnSuccess} />);
    fireEvent.click(screen.getByRole("button", { name: /open project/i }));

    expect(mockNavigate).toHaveBeenCalledWith(`/projects/${project.id}`);
  });
});
