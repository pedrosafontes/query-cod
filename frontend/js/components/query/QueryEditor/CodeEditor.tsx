import MonacoEditor, { Monaco } from "@monaco-editor/react";
import { editor } from "monaco-editor";

import { Spinner } from "@/components/ui/spinner";
import { registerLatexLanguage } from "lib/monaco-latex";
import { cn } from "lib/utils";

type CodeEditorProps = {
  value?: string;
  onChange?: (value?: string) => void;
  language?: string;
  className?: string;
  options?: editor.IStandaloneEditorConstructionOptions;
  onMount?: (editor: editor.IStandaloneCodeEditor, monaco: Monaco) => void;
};

const CodeEditor = ({
  value,
  onChange,
  language,
  className,
  options = {},
  onMount,
}: CodeEditorProps) => (
  <MonacoEditor
    beforeMount={(monaco) => {
      registerLatexLanguage(monaco);
    }}
    defaultLanguage={language}
    loading={<Spinner className="text-gray-400" size="small" />}
    options={{
      fontSize: 14,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      wordWrap: "on",
      tabSize: 2,
      formatOnType: true,
      formatOnPaste: true,
      fixedOverflowWidgets: true,
      ...options,
    }}
    theme="vs-light"
    value={value}
    wrapperProps={{ className: cn(className, "!w-auto") }}
    onChange={onChange}
    onMount={onMount}
  />
);

export default CodeEditor;
