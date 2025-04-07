import { ArrowRight, Pencil, Trash } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";

import { Project, ProjectsService } from "../api";
import { useToast } from "../hooks/use-toast";

import ProjectForm from "./ProjectForm";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";

type ProjectActionsProps = {
  project: Project;
  onSuccess: () => void;
};

const ProjectActions = ({ project, onSuccess }: ProjectActionsProps) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const deleteProject = async (id: number) => {
    try {
      await ProjectsService.projectsDestroy({ id });
      onSuccess();
      toast({ title: "Project deleted" });
    } catch (error) {
      console.error("Failed to delete project:", error);
    }
  };

  return (
    <div className="flex justify-end gap-2">
      <Button
        className="text-destructive"
        size="sm"
        variant="outline"
        onClick={() => deleteProject(project.id)}
      >
        <Trash />
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <Button size="sm" variant="outline">
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
        size="sm"
        variant="outline"
        onClick={() => navigate(`/projects/${project.id}`)}
      >
        <ArrowRight />
        Open
      </Button>
    </div>
  );
};

export default ProjectActions;
