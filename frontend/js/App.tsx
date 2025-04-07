import * as Sentry from "@sentry/react";
import cookie from "cookie";
import { BrowserRouter, Routes, Route } from "react-router";

import { Toaster } from "@/components/ui/toaster";

import { OpenAPI } from "./api";
import AuthenticatedLayout from "./components/AuthenticatedLayout";
import PrivateRoute from "./components/PrivateRoute";
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
      <Routes>
        <Route element={<LoginPage />} path="/login" />
        <Route element={<SignupPage />} path="/signup" />
        <Route element={<PrivateRoute />}>
          <Route element={<AuthenticatedLayout />}>
            <Route element={<ProjectsPage />} path="/projects" />
            <Route element={<ProjectPage />} path="/projects/:projectId" />
          </Route>
        </Route>
      </Routes>
      <Toaster />
    </BrowserRouter>
  </Sentry.ErrorBoundary>
);

export default App;
