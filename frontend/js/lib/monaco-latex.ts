import { Monaco } from "@monaco-editor/react";
import latex from "monaco-latex";

export function registerLatexLanguage(monaco: Monaco): void {
  monaco.languages.register({ id: "latex" });
  monaco.languages.setMonarchTokensProvider("latex", latex);
}
