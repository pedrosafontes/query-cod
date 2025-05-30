import * as Sentry from "@sentry/react";
import cookie from "cookie";
import { BrowserRouter, Routes, Route, Navigate } from "react-router";

import { Toaster } from "@/components/ui/toaster";

import { OpenAPI } from "./api";
import AuthenticatedLayout from "./components/layout/AuthenticatedLayout";
import AuthRoute from "./components/route/AuthRoute";
import PrivateRoute from "./components/route/PrivateRoute";
import { AuthProvider } from "./contexts/AuthContext";
import ExercisePage from "./pages/ExercisePage";
import ExercisesPage from "./pages/ExercisesPage";
import LoginPage from "./pages/LoginPage";
import ProjectPage from "./pages/ProjectPage";
import ProjectsPage from "./pages/ProjectsPage";
import SignupPage from "./pages/SignupPage";

OpenAPI.interceptors.request.use((request) => {
  const { csrftoken } = cookie.parse(document.cookie);
  if (request.headers && csrftoken) {
    request.headers["X-CSRFTOKEN"] = csrftoken;
  }
  return request;
});

const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<Navigate replace to="/login" />} path="/" />
          <Route element={<AuthRoute />}>
            <Route element={<LoginPage />} path="/login" />
            <Route element={<SignupPage />} path="/signup" />
          </Route>
          <Route element={<PrivateRoute />}>
            <Route element={<AuthenticatedLayout />}>
              <Route element={<ProjectsPage />} path="/projects" />
              <Route element={<ProjectPage />} path="/projects/:projectId" />
              <Route element={<ExercisesPage />} path="/exercises" />
              <Route element={<ExercisePage />} path="/exercises/:exerciseId" />
            </Route>
          </Route>
        </Routes>
        <Toaster />
      </AuthProvider>
    </BrowserRouter>
  </Sentry.ErrorBoundary>
);

export default App;
