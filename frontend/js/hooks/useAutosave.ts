import debounce from "lodash.debounce";
import { useEffect, useRef, useState } from "react";

export type Status = "idle" | "saving" | "saved" | "error";

export function useAutosave({
  data,
  onSave,
  delay = 1000,
}: {
  data: string | undefined;
  onSave: (value: string) => Promise<void>;
  delay?: number;
}) {
  const [status, setStatus] = useState<Status>("idle");
  const lastSaved = useRef<string | undefined>(data);
  const current = useRef<string | undefined>(data);

  const save = async () => {
    const valueToSave = current.current;

    if (valueToSave === undefined || valueToSave === lastSaved.current) return;

    setStatus("saving");
    try {
      await onSave(valueToSave);

      // eslint-disable-next-line require-atomic-updates
      lastSaved.current = valueToSave;

      setStatus("saved");
      setTimeout(() => setStatus("idle"), 1500);
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
