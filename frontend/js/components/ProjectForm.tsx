import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState, useEffect } from "react";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from "@/components/ui/select";

import {
  Database,
  DatabasesService,
  Project,
  ProjectsService
} from "../api";

type ProjectFormValues = {
  name: string;
  database_id: number;
};

const projectSchema = z.object({
  name: z.string().nonempty("Project name is required"),
  database_id: z.number(),
});

type ProjectFormProps = {
  onSuccess?: () => void;
};

const ProjectForm = ({ onSuccess }: ProjectFormProps) => {
  const [databases, setDatabases] = useState<Database[]>([]);
  const [loadingDatabases, setLoadingDatabases] = useState(true);

  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: "",
      database_id: undefined,
    },
  });

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
      await ProjectsService.projectsCreate({ requestBody: values as Project });
      form.reset();
      onSuccess?.();
    } catch (err) {
      console.error("Project creation failed", err);
      form.setError("root", {
        type: "manual",
        message: "Failed to create project. Please try again.",
      });
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-4"
      >
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
          name="database_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database</FormLabel>
              <FormControl>
                <Select
                  disabled={loadingDatabases}
                  onValueChange={(value) => field.onChange(Number(value))}
                  value={field.value?.toString() || ""}
                >
                  <SelectTrigger>
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

        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating Project..." : "Create Project"}
        </Button>
      </form>
    </Form>
  );
};

export default ProjectForm;
