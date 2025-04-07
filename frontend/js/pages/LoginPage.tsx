import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router";
import { z } from "zod";

import { AuthService } from "@/api";
import type { Login } from "@/api/types.gen";
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

type LoginFormValues = Login;

const loginSchema = z.object({
  username: z.string().email("Invalid email"),
  password: z.string().nonempty("Password is required"),
});

export default function LoginPage() {
  const navigate = useNavigate();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      await AuthService.authLoginCreate({ requestBody: values });
      navigate("/projects");
    } catch (err) {
      form.setError("password", { message: "Invalid credentials" });
    }
  };

  return (
    <div className="max-w-sm mx-auto py-10">
      <h1 className="text-xl font-semibold mb-3 text-center">Log in</h1>
      <Form {...form}>
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    placeholder="you@example.com"
                    type="email"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input placeholder="••••••••" type="password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            className="w-full"
            disabled={form.formState.isSubmitting}
            type="submit"
          >
            {form.formState.isSubmitting ? "Logging in..." : "Log in"}
          </Button>
        </form>
      </Form>
      <p className="text-sm text-center mt-4">
        Don't have an account?{" "}
        <Link to="/signup" className="hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
