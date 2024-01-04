export interface FormRules<RegisterField = any> {
  required?: {
    value: boolean;
    message: string;
  };
  min?: {
    value: number | string;
    message: string;
  };
  max?: {
    value: number | string;
    message: string;
  };
  minLength?: {
    value: number;
    message: string;
  };
  maxLength?: {
    value: number;
    message: string;
  };
  pattern?: {
    value: RegExp;
    message: string;
  };
  validate?: (input: string, values: RegisterField) => boolean | string;
}

export interface Option<T = string> {
  label: string;
  value: T;
}

export const INPUT_TYPE = Object.freeze({
  TEXT: 'text',
  MULTILINE: 'multiline',
  SELECT: 'select',
});

type InputSchema = typeof INPUT_TYPE;
type InputKeys = keyof typeof INPUT_TYPE;
export type InputTypes = InputSchema[InputKeys];
