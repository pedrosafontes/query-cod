import debounce from "lodash.debounce";
import { useEffect, useRef, useState } from "react";

type Status = "idle" | "saving" | "saved" | "error";

export function useAutosave({
  data,
  onSave,
  delay = 1000,
}: {
  data: string;
  onSave: (value: string) => Promise<void>;
  delay?: number;
}) {
  const [status, setStatus] = useState<Status>("idle");
  const lastSaved = useRef<string>(data);
  const current = useRef<string>(data);

  const save = async () => {
    if (current.current === lastSaved.current) return;

    setStatus("saving");
    try {
      await onSave(current.current);
      lastSaved.current = current.current;
      setStatus("saved");

      setTimeout(() => setStatus("idle"), 1500); // reset after 1.5s
    } catch (e) {
      setStatus("error");
    }
  };

  const debouncedSave = useRef(debounce(save, delay)).current;

  useEffect(() => {
    current.current = data;

    if (current.current !== lastSaved.current) {
      setStatus("saving");
    }

    debouncedSave();
    return () => debouncedSave.cancel();
  }, [data, debouncedSave]);

  return status;
}
