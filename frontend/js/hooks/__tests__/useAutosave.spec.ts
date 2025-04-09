import { renderHook, act } from "@testing-library/react";

import { useAutosave } from "../useAutosave";

jest.useFakeTimers();

describe("useAutosave", () => {
  let onSave: jest.Mock;

  beforeEach(() => {
    onSave = jest.fn().mockResolvedValue(undefined);
  });

  test("should return 'idle' initially", () => {
    const { result } = renderHook(() =>
      useAutosave({ data: "initial", onSave, delay: 1000 }),
    );
    expect(result.current).toBe("idle");
  });

  test("calls onSave after data changes and debounce delay", async () => {
    const { result, rerender } = renderHook(
      ({ data }) => useAutosave({ data, onSave, delay: 1000 }),
      { initialProps: { data: "initial" } },
    );

    // Update the data value
    act(() => {
      rerender({ data: "new value" });
    });

    expect(result.current).toBe("saving");

    // Advance timer by 1000ms (debounce delay)
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    expect(onSave).toHaveBeenCalledWith("new value");

    await act(async () => {
      await Promise.resolve();
    });
    expect(result.current).toBe("saved");

    // After 1500ms the status should revert to "idle"
    await act(async () => {
      jest.advanceTimersByTime(1500);
    });
    expect(result.current).toBe("idle");
  });

  test("does not call onSave if the data has not changed", async () => {
    const { result, rerender } = renderHook(
      ({ data }) => useAutosave({ data, onSave, delay: 1000 }),
      { initialProps: { data: "initial" } },
    );

    act(() => {
      // Re-render with the same data
      rerender({ data: "initial" });
      jest.advanceTimersByTime(1000);
    });

    expect(onSave).not.toHaveBeenCalled();
    expect(result.current).toBe("idle");
  });

  test("sets status to 'error' if onSave fails", async () => {
    onSave.mockRejectedValueOnce(new Error("failure"));

    const { result, rerender } = renderHook(
      ({ data }) => useAutosave({ data, onSave, delay: 1000 }),
      { initialProps: { data: "initial" } },
    );

    act(() => {
      // Update data to trigger a save
      rerender({ data: "error value" });
    });

    act(() => {
      jest.advanceTimersByTime(1000);
    });

    await act(async () => {
      await Promise.resolve();
    });
    expect(result.current).toBe("error");
  });
});
