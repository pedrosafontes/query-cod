import type { ColumnDef } from "@tanstack/react-table";
import { formatDistanceToNow } from "date-fns";
import { Plus } from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ProjectsService, type Project } from "api";
import { DataTable } from "components/common/DataTable";
import ProjectActions from "components/project/ProjectActions";
import ProjectForm from "components/project/ProjectForm";
import { useErrorToast } from "hooks/useErrorToast";

const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const toast = useErrorToast();

  const fetchProjects = useCallback(async () => {
    try {
      const response = await ProjectsService.projectsList();
      setProjects(response);
    } catch (error) {
      toast({
        title: "Error loading projects",
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
    },
    {
      accessorKey: "database.name",
      header: "Database",
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

  const navigate = useNavigate();

  const handleRowClick = (project: Project) => {
    navigate(`/projects/${project.id}`);
  };

  return (
    <div className="p-6 h-screen overflow-auto">
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
      <DataTable
        columns={columns}
        data={projects}
        loading={loading}
        pageSize={8}
        onRowClick={handleRowClick}
      />
    </div>
  );
};

export default ProjectsPage;
