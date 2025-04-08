import type { ColumnDef } from "@tanstack/react-table";
import { formatDistanceToNow } from "date-fns";
import { Plus } from "lucide-react";
import { useEffect, useState, useCallback } from "react";

import { ProjectsService, type Project } from "@/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { DataTable } from "../components/DataTable";
import ProjectActions from "../components/ProjectActions";
import ProjectForm from "../components/ProjectForm";
import { useToast } from "../hooks/use-toast";

const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { toast } = useToast();

  const fetchProjects = useCallback(async () => {
    try {
      const response = await ProjectsService.projectsList();
      setProjects(response.results);
    } catch (error) {
      toast({
        title: "Error loading projects",
        variant: "destructive",
      });
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
      cell: ({ row }) => row.original.name,
    },
    {
      accessorKey: "database",
      header: "Database",
      cell: ({ row }) => row.original.database.name,
    },
    {
      accessorKey: "last_modified",
      header: "Last modified",
      cell: ({ row }) =>
        formatDistanceToNow(new Date(row.original.last_modified), {
          addSuffix: true,
        }),
    },
    {
      accessorKey: "created",
      header: "Created",
      cell: ({ row }) =>
        formatDistanceToNow(new Date(row.original.created), {
          addSuffix: true,
        }),
    },
    {
      id: "actions",
      header: () => <div className="text-right">Actions</div>,
      cell: ({ row }) => (
        <ProjectActions project={row.original} onSuccess={fetchProjects} />
      ),
    },
  ];

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
      <DataTable columns={columns} data={projects} loading={loading} />
    </div>
  );
};

export default ProjectsPage;
