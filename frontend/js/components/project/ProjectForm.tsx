import { zodResolver } from "@hookform/resolvers/zod";
import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

import {
  DatabaseSummary as Database,
  DatabasesService,
  Project,
  ProjectsService,
} from "../../api";

type ProjectFormValues = {
  name: string;
  databaseId: number;
};

const projectSchema = z.object({
  name: z.string().nonempty("Project name is required"),
  databaseId: z.number(),
});

export type ProjectFormProps = {
  onSuccess?: () => void;
  project?: Project;
};

const ProjectForm = ({ onSuccess, project }: ProjectFormProps) => {
  const [databases, setDatabases] = useState<Database[]>([]);
  const [loadingDatabases, setLoadingDatabases] = useState(true);

  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: project?.name || "",
      databaseId: project?.database.id || undefined,
    },
  });

  useEffect(() => {
    if (project) {
      form.reset({
        name: project.name,
        databaseId: project.database.id,
      });
    }
  }, [project, form]);

  const fetchDatabases = async () => {
    try {
      const response = await DatabasesService.databasesList();
      setDatabases(response);
    } catch (err) {
      console.error("Failed to fetch databases", err);
    } finally {
      setLoadingDatabases(false);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, []);

  const onSubmit = async (values: ProjectFormValues) => {
    try {
      if (project?.id) {
        await ProjectsService.projectsPartialUpdate({
          id: project.id,
          requestBody: values,
        });
      } else {
        await ProjectsService.projectsCreate({
          requestBody: {
            name: values.name,
            database_id: values.databaseId,
          } as Project,
        });
      }

      form.reset();
      onSuccess?.();
    } catch (err) {
      form.setError("root", {
        type: "manual",
        message: "Failed to submit project. Please try again.",
      });
    }
  };

  return (
    <Form {...form}>
      <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="databaseId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database</FormLabel>
              <FormControl>
                <Select
                  disabled={loadingDatabases}
                  value={field.value?.toString() || ""}
                  onValueChange={(value) => field.onChange(Number(value))}
                >
                  <SelectTrigger aria-label="Database">
                    <SelectValue placeholder="Select a database" />
                  </SelectTrigger>
                  <SelectContent>
                    {databases.map((db) => (
                      <SelectItem key={db.id} value={db.id.toString()}>
                        {db.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {form.formState.errors.root && (
          <div className="text-sm text-destructive">
            {form.formState.errors.root.message}
          </div>
        )}
        <div className="flex justify-end">
          <Button disabled={form.formState.isSubmitting} type="submit">
            {form.formState.isSubmitting
              ? project
                ? "Updating..."
                : "Creating..."
              : project
                ? "Update Project"
                : "Create Project"}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default ProjectForm;
