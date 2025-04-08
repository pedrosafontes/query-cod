import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router";
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
import { AuthService, UserCreate } from "api";
import { useAuth } from "contexts/AuthContext";

type SignupFormValues = Omit<UserCreate, "id"> & {
  confirmPassword: string;
};

const signupSchema = z
  .object({
    email: z.string().email("Invalid email"),
    password: z.string().nonempty("Password is required"),
    confirmPassword: z.string().nonempty("Password confirmation is required"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords do not match",
  });

const SignupPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const form = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
  });

  const onSubmit = async ({ email, password }: SignupFormValues) => {
    try {
      await AuthService.authUsersCreate({
        requestBody: {
          email,
          password,
        } as UserCreate,
      });
      login(email, password);
      navigate("/projects");
    } catch (err) {
      form.setError("email", { message: "Signup failed." });
    }
  };

  return (
    <div className="max-w-sm mx-auto py-10">
      <h1 className="text-xl font-semibold mb-3 text-center">Sign up</h1>
      <Form {...form}>
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          <FormField
            control={form.control}
            name="email"
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
          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirm Password</FormLabel>
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
            {form.formState.isSubmitting ? "Creating account..." : "Sign up"}
          </Button>
        </form>
      </Form>
      <p className="text-sm text-center mt-4">
        Already have an account?{" "}
        <Link className="hover:underline" to="/login">
          Log in
        </Link>
      </p>
    </div>
  );
};

export default SignupPage;
