export class MathfieldElement {
  value = "";

  // eslint-disable-next-line class-methods-use-this, no-empty-function
  setOptions() {}

  executeCommand = jest.fn();

  getValue = () => this.value;
}
