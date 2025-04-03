import * as Sentry from "@sentry/react";
import cookie from "cookie";

import { OpenAPI } from "./api";
import QueriesExplorer from "./pages/QueriesExplorer";
import { Toaster } from "@/components/ui/toaster"

OpenAPI.interceptors.request.use((request) => {
  const { csrftoken } = cookie.parse(document.cookie);
  if (request.headers && csrftoken) {
    request.headers["X-CSRFTOKEN"] = csrftoken;
  }
  return request;
});

const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <QueriesExplorer />
    <Toaster />
  </Sentry.ErrorBoundary>
);

export default App;
