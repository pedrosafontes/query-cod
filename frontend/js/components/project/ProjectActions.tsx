import { ArrowRight, Pencil, Trash } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";

import { useErrorToast } from "hooks/useErrorToast";

import { Project, ProjectsService } from "../../api";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";

import ProjectForm from "./ProjectForm";

type ProjectActionsProps = {
  project: Project;
  onSuccess: () => void;
};

const ProjectActions = ({ project, onSuccess }: ProjectActionsProps) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const toast = useErrorToast();

  const deleteProject = async (id: number) => {
    try {
      await ProjectsService.projectsDestroy({ id });
      onSuccess();
    } catch (error) {
      toast({
        title: "Error deleting project",
      });
    }
  };

  return (
    <div className="flex justify-end gap-2">
      <Button
        aria-label="Delete Project"
        className="text-destructive"
        size="sm"
        variant="outline"
        onClick={() => deleteProject(project.id)}
      >
        <Trash />
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <Button aria-label="Edit Project" size="sm" variant="outline">
            <Pencil />
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
          </DialogHeader>
          <ProjectForm
            project={project}
            onSuccess={() => {
              onSuccess();
              setDialogOpen(false);
            }}
          />
        </DialogContent>
      </Dialog>

      <Button
        aria-label="Open Project"
        size="sm"
        variant="secondary"
        className="border"
        onClick={() => navigate(`/projects/${project.id}`)}
      >
        <ArrowRight />
        Open
      </Button>
    </div>
  );
};

export default ProjectActions;
