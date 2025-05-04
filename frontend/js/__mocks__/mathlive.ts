export class MathfieldElement {
  value = "";

  // eslint-disable-next-line class-methods-use-this, no-empty-function
  setOptions = jest.fn();

  executeCommand = jest.fn();

  getValue = jest.fn();
}

if (!customElements.get("math-field")) {
  customElements.define(
    "math-field",
    class extends HTMLElement {
      value = "";

      getValue = jest.fn();

      setValue = jest.fn();

      executeCommand = jest.fn();
    },
  );
}
