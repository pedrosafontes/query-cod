import * as Sentry from "@sentry/react";
import cookie from "cookie";
import { BrowserRouter, Routes, Route } from "react-router";

import { Toaster } from "@/components/ui/toaster";

import { OpenAPI } from "./api";
import AuthenticatedLayout from "./components/AuthenticatedLayout";
import ProjectsPage from "./pages/ProjectsPage";
import QueriesExplorer from "./pages/QueriesExplorer";

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
        <Route element={<AuthenticatedLayout />}>
          <Route element={<ProjectsPage />} path="/projects" />
          <Route element={<QueriesExplorer />} path="/projects/:projectId" />
        </Route>
      </Routes>
      <Toaster />
    </BrowserRouter>
  </Sentry.ErrorBoundary>
);

export default App;
