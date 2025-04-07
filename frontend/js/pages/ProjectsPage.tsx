import type { ColumnDef } from "@tanstack/react-table";
import { Loader2, Plus } from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router";

import { ProjectsService, type Project } from "@/api";
import { Button } from "@/components/ui/button";
import { DataTable } from "../components/DataTable";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog";
import ProjectForm from "../components/ProjectForm";

const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();

  const fetchProjects = useCallback(async () => {
    try {
      const response = await ProjectsService.projectsList();
      setProjects(response.results || []);
    } catch (error) {
      console.error("Failed to load projects:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const columns: ColumnDef<Project>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <span>{row.original.name}</span>,
    },
    {
      accessorKey: "database",
      header: "Database",
      cell: ({ row }) => <span>{row.original.database}</span>,
    },
    {
      id: "actions",
      header: () => <div className="text-right">Actions</div>,
      cell: ({ row }) => (
        <div className="text-right">
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate(`/projects/${row.original.id}`)}
          >
            Open
          </Button>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Loading projects...</span>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-end mb-4">
        <h1 className="text-xl font-semibold">Projects</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus /> New Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Project</DialogTitle>
            </DialogHeader>
            <ProjectForm
              onSuccess={() => {
                fetchProjects();
                setDialogOpen(false);
              }}
            />
          </DialogContent>
        </Dialog>
      </div>
      <DataTable columns={columns} data={projects} />
    </div>
  );
};

export default ProjectsPage;
